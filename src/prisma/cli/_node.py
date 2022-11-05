from __future__ import annotations

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, IO, Union, Any, Mapping, cast
from typing_extensions import Literal

from pydantic.typing import get_args

from .. import config
from .._proxy import LazyProxy
from ..binaries import platform
from ..errors import PrismaError

if TYPE_CHECKING:
    # TODO
    import nodejs  # type: ignore
    import nodejs.node  # type: ignore
    import nodejs.npm  # type: ignore
else:
    try:
        import nodejs
    except ImportError:
        nodejs = None


log: logging.Logger = logging.getLogger(__name__)
File = Union[int, IO[Any]]
Target = Literal['node', 'npm']


class UnknownTargetError(PrismaError):
    def __init__(self, *, target: str) -> None:
        super().__init__(
            f'Unknown target: {target}; Valid choices are: {", ".join(get_args(cast(type, Target)))}'
        )


class Strategy(ABC):
    resolver: Literal['nodejs-bin', 'global', 'nodeenv']

    # TODO: support more options
    def run(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        stdout: File | None = None,
        stderr: File | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        """Call the underlying Node.js binary.

        The interface for this function is very similar to `subprocess.run()`.
        """
        return self.__run__(
            *args,
            check=check,
            cwd=cwd,
            stdout=stdout,
            stderr=stderr,
            env=_update_path_env(
                env=env,
                target_bin=self.target_bin,
            ),
        )

    @abstractmethod
    def __run__(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        stdout: File | None = None,
        stderr: File | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        """Call the underlying Node.js binary.

        This should not be directly accessed, the `run()` function should be used instead.
        """

    @property
    @abstractmethod
    def target_bin(self) -> Path:
        """Property containing the location of the `bin` directory for the resolved node installation.

        This is used to dynamically alter the `PATH` environment variable to give the appearance that Node
        is installed globally on the machine as this is a requirement of Prisma's installation step, see this
        comment for more context: https://github.com/RobertCraigie/prisma-client-py/pull/454#issuecomment-1280059779
        """
        ...


class NodeBinaryStrategy(Strategy):
    resolver: Literal['global', 'nodeenv']

    def __init__(
        self,
        *,
        path: Path,
        resolver: Literal['global', 'nodeenv'],
    ) -> None:
        self.path = path
        self.resolver = resolver

    @property
    def target_bin(self) -> Path:
        return self.path.parent

    def __run__(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        stdout: File | None = None,
        stderr: File | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        print('--- debug ---')
        if platform.name() == 'windows':
            for p in self.path.parent.rglob('*'):
                if 'node_modules' in str(p):
                    continue

                print(p)
        print('--- end ---')
        print('-- list dir --')
        for p in self.path.parent.iterdir():
            print(p)
        print('-- end --')

        path = str(self.path.absolute())
        log.debug('Executing binary at %s with args: %s', path, args)
        return subprocess.run(
            [path, *args],
            check=check,
            cwd=cwd,
            env=env,
            stdout=stdout,
            stderr=stderr,
        )

    @classmethod
    def resolve(cls, target: Target) -> NodeBinaryStrategy:
        path = None
        if config.use_global_node:
            # TODO: this should check the version
            path = _get_global_binary(target)

        if path is not None:
            return NodeBinaryStrategy(path=path, resolver='global')

        return NodeBinaryStrategy.from_nodeenv(target)

    @classmethod
    def from_nodeenv(cls, target: Target) -> NodeBinaryStrategy:
        cache_dir = config.nodeenv_cache_dir.absolute()
        if cache_dir.exists():
            log.debug(
                'Skipping nodeenv installation as it already exists at %s',
                cache_dir,
            )
        else:
            log.debug('Installing nodeenv to %s', cache_dir)
            subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'nodeenv',
                    str(cache_dir),
                    *config.nodeenv_extra_args,
                ],
                check=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            if platform.name() == 'windows':
                cache_dir.joinpath('node').symlink_to('node.exe')

        if not cache_dir.exists():
            raise RuntimeError(
                'Could not install nodeenv to the expected directory; See the output above for more details.'
            )

        # TODO: what hapens on cygwin?
        if platform.name() == 'windows':
            bin_dir = cache_dir / 'Scripts'
            if target == 'node':
                path = bin_dir / 'node.exe'
            else:
                path = bin_dir / f'{target}.cmd'
        else:
            path = cache_dir / 'bin' / target

        if target == 'npm':
            return cls(path=path, resolver='nodeenv')
        elif target == 'node':
            return cls(path=path, resolver='nodeenv')
        else:
            raise UnknownTargetError(target=target)


class NodeJSPythonStrategy(Strategy):
    target: Target
    resolver: Literal['nodejs-bin']

    def __init__(self, *, target: Target) -> None:
        self.target = target
        self.resolver = 'nodejs-bin'

    def __run__(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        stdout: File | None = None,
        stderr: File | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        func = None
        if self.target == 'node':
            func = nodejs.node.run
        elif self.target == 'npm':
            func = nodejs.npm.run
        else:
            raise UnknownTargetError(target=self.target)

        # TODO
        return func(  #  type: ignore
            args,
            check=check,
            cwd=cwd,
            env=env,
            stdout=stdout,
            stderr=stderr,
        )

    @property
    def target_bin(self) -> Path:
        return Path(nodejs.node.path).parent


Node = Union[NodeJSPythonStrategy, NodeBinaryStrategy]


def resolve(target: Target) -> Node:
    if target not in {'node', 'npm'}:
        raise UnknownTargetError(target=target)

    if config.use_nodejs_bin:
        log.debug('Checking if nodejs-bin is installed')
        if nodejs is not None:
            log.debug('Using nodejs-bin with version: %s', nodejs.node_version)
            return NodeJSPythonStrategy(target=target)

    return NodeBinaryStrategy.resolve(target)


def _update_path_env(
    *,
    env: Mapping[str, str] | None,
    target_bin: Path,
    sep: str = os.pathsep,
) -> dict[str, str]:
    """Returns a modified version of `os.environ` with the `PATH` environment variable updated
    to include the location of the downloaded Node binaries.
    """
    if env is None:
        env = dict(os.environ)

    assert target_bin.exists(), 'Target `bin` directory does not exist'

    path = env.get('PATH', '') or os.environ.get('PATH', '')
    if path:
        # handle the case where the PATH already ends with the `:` separator (this probably shouldn't happen)
        if path.endswith(sep):
            path = f'{path}{target_bin.absolute()}'
        else:
            path = f'{path}{sep}{target_bin.absolute()}'
    else:
        # handle the case where there is no PATH set (unlikely / impossible to actually happen?)
        path = str(target_bin.absolute())

    return {**env, 'PATH': path}


def _get_global_binary(target: Target) -> Path | None:
    log.debug('Checking for global target binary: %s', target)

    which = shutil.which(target)
    if which is not None:
        log.debug('Found global binary at: %s', which)

        path = Path(which)
        if path.exists():
            log.debug('Global binary exists at: %s', which)
            return path

    log.debug('Global target binary: %s not found', target)
    return None


class LazyBinaryProxy(LazyProxy[Node]):
    target: Target

    def __init__(self, target: Target) -> None:
        super().__init__()
        self.target = target

    def __load__(self) -> Node:
        return resolve(self.target)


npm = cast(Node, LazyBinaryProxy('npm'))
node = cast(Node, LazyBinaryProxy('node'))
