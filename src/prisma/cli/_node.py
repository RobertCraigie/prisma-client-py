from __future__ import annotations
from enum import Enum, auto

import sys
import shutil
import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, IO, Union, Any, Mapping
from typing_extensions import Literal

from .._compat import cached_property

if TYPE_CHECKING:
    import nodejs
    import nodejs.npm
else:
    try:
        import nodejs
    except ImportError:
        nodejs = None


log: logging.Logger = logging.getLogger(__name__)
File = Union[int, IO[Any]]
Target = Literal['node', 'npm']
NODEENV_DIR = Path.home() / '.cache' / 'prisma-nodeenv'

# Support configuring
USE_GLOBAL_NODE = True


class Command:
    target: Target

    def __init__(self, target: Target) -> None:
        self.target = target

    # TODO: support more args
    def run(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        stdout: File | None = None,
        stderr: File | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        self.install()

        func = None
        target = self.target
        binary = self.binary
        strategy = binary.strategy
        if strategy == Strategy.NODEJS_BIN:
            if target == 'node':
                func = nodejs.node.run
            elif target == 'npm':
                func = nodejs.npm.run
            else:
                raise RuntimeError('TODO')
        elif strategy == Strategy.GLOBAL:
            func = subprocess.run
        elif strategy == Strategy.NODEENV:
            func = subprocess.run
        else:
            raise RuntimeError('TODO')

        return func(
            [str(self.path.absolute()), *args],
            check=check,
            cwd=cwd,
            env=env,
            stdout=stdout,
            stderr=stderr,
        )

    @property
    def path(self) -> Path:
        return self.binary.path

    def install(self) -> None:
        binary = self.binary
        if binary.strategy == Strategy.NODEJS_BIN:
            return

        path = binary.path
        assert path is not None
        if path.exists():
            return

        subprocess.run(
            [sys.executable, '-m', 'nodeenv', str(NODEENV_DIR.absolute())],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        if not path.exists():
            raise RuntimeError('TODO: error message')

    def resolve(self) -> None:
        ...

    @cached_property
    def binary(self) -> Binary:
        # TODO: heavily log
        # TODO: add config option to disable
        # if nodejs is not None:
        #     return Binary(strategy=Strategy.NODEJS_BIN)

        path = None
        if USE_GLOBAL_NODE:
            # TODO: this should check the version
            path = _get_global_binary(self.target)

        if path is not None:
            return Binary(strategy=Strategy.GLOBAL, path=path)

        target = self.target
        if target == 'npm':
            return Binary(NODEENV_DIR / 'bin' / 'npm')
        elif target == 'node':
            return Binary(NODEENV_DIR / 'bin' / 'node')
        else:
            # TODO: include list of valid targets
            raise ValueError(f'Unknown target: {target}')


# TODO: refactor
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


class Strategy(int, Enum):
    GLOBAL = auto()
    NODEENV = auto()
    # TODO: proper support
    NODEJS_BIN = auto()


class Binary:
    path: Path | None
    strategy: Strategy

    def __init__(
        self,
        *,
        path: Path | None = None,
        strategy: Strategy,
    ) -> None:
        self.path = path
        self.strategy = strategy

    @classmethod
    def resolve(cls, target: Target) -> Binary:
        ...


# TODO: this changes on different platforms
npm = Command('npm')
node = Command('node')
