from __future__ import annotations

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
    # TODO: support more options
    @abstractmethod
    def run(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        stdout: File | None = None,
        stderr: File | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        ...


class NodeBinaryStrategy(Strategy):
    def __init__(self, *, path: Path) -> None:
        self.path = path

    def run(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        stdout: File | None = None,
        stderr: File | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [str(self.path.absolute()), *args],
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
            return NodeBinaryStrategy(path=path)

        return NodeBinaryStrategy.from_nodeenv(target)

    @classmethod
    def from_nodeenv(cls, target: Target) -> NodeBinaryStrategy:
        path = config.nodeenv_cache_dir.absolute()
        if path.exists():
            log.debug(
                'Skipping nodeenv installation as it already exists at %s',
                path,
            )
        else:
            log.debug('Installing nodeenv to %s', path)
            subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'nodeenv',
                    str(path),
                    *config.nodeenv_extra_args,
                ],
                check=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

        if not path.exists():
            raise RuntimeError(
                'Could not install nodeenv to the expected directory; See the output above for more details.'
            )

        # TODO: what hapens on cygwin?
        # TODO: needs .exe postfix?
        if platform.name() == 'windows':
            bin_dir = path / 'Scripts'
        else:
            bin_dir = path / 'bin'

        if target == 'npm':
            return cls(path=bin_dir / 'npm')
        elif target == 'node':
            return cls(path=bin_dir / 'node')
        else:
            raise UnknownTargetError(target=target)


class NodeJSPythonStrategy(Strategy):
    target: Target

    def __init__(self, *, target: Target) -> None:
        self.target = target

    def run(
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
