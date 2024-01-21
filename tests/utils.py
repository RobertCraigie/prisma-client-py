from __future__ import annotations

import os
import sys
import uuid
import inspect
import textwrap
import contextlib
import subprocess
from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Tuple,
    Union,
    Mapping,
    Callable,
    Iterator,
    Optional,
    cast,
)
from pathlib import Path
from typing_extensions import override

import click
import pytest
from click.testing import Result, CliRunner

from prisma import _config
from lib.utils import escape_path
from prisma.cli import main
from prisma._proxy import LazyProxy
from prisma._types import FuncType
from prisma.binaries import platform
from prisma.generator.utils import copy_tree
from prisma.generator.generator import BASE_PACKAGE_DIR

if TYPE_CHECKING:
    from _pytest.pytester import Pytester, RunResult
    from _pytest.monkeypatch import MonkeyPatch


CapturedArgs = Tuple[Tuple[object, ...], Mapping[str, object]]


# as we are generating new modules we need to clear them from
# the module cache so that python actually picks them up
# when we import them again, however we also have to ignore
# any prisma.generator modules as we rely on the import caching
# mechanism for loading partial model types
IMPORT_RELOADER = """
import sys
for name in sys.modules.copy():
    if 'prisma' in name and 'generator' not in name:
        sys.modules.pop(name, None)
"""

DEFAULT_GENERATOR = """
generator db {{
  provider = "coverage run -m prisma"
  output = "{output}"
  {options}
}}

"""

SCHEMA_HEADER = (
    """
datasource db {{
  provider = "sqlite"
  url      = "file:dev.db"
}}

"""
    + DEFAULT_GENERATOR
)

DEFAULT_SCHEMA = (
    SCHEMA_HEADER
    + """
model User {{
  id           String   @id @default(cuid())
  created_at   DateTime @default(now())
  updated_at   DateTime @updatedAt
  name         String
}}
"""
)


class Runner:
    def __init__(self, patcher: 'MonkeyPatch') -> None:
        self._runner = CliRunner()
        self._patcher = patcher
        self.default_cli: Optional[click.Command] = None
        self.patch_subprocess()

    def invoke(
        self,
        args: Optional[List[str]] = None,
        cli: Optional[click.Command] = None,
        **kwargs: Any,
    ) -> Result:
        default_args: Optional[List[str]] = None

        if cli is not None:
            default_args = args
        elif self.default_cli is not None:
            cli = self.default_cli
            default_args = args
        else:

            def _cli() -> None:
                if args is not None:  # pragma: no branch
                    # fake invocation context
                    args.insert(0, 'prisma')

                main(args, use_handler=False, do_cleanup=False)

            cli = click.command()(_cli)

            # we don't pass any args to click as we need to parse them ourselves
            default_args = []

        return self._runner.invoke(cli, default_args, **kwargs)

    def patch_subprocess(self) -> None:
        """As we can't pass a fd from something like io.TextIO to a subprocess
        we need to override the subprocess.run method to pipe the output and then
        print the output ourselves so that it can be captured by anything higher in
        call stack.
        """

        def _patched_subprocess_run(*args: Any, **kwargs: Any) -> 'subprocess.CompletedProcess[str]':
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            kwargs['encoding'] = sys.getdefaultencoding()

            process = old_subprocess_run(*args, **kwargs)

            assert isinstance(process.stdout, str)

            print(process.stdout)
            print(process.stderr, file=sys.stderr)
            return process

        old_subprocess_run = subprocess.run
        self._patcher.setattr(subprocess, 'run', _patched_subprocess_run, raising=True)


class Testdir:
    __test__ = False
    SCHEMA_HEADER = SCHEMA_HEADER
    default_schema = DEFAULT_SCHEMA
    default_generator = DEFAULT_GENERATOR

    def __init__(self, pytester: Pytester) -> None:
        self.pytester = pytester

    def _make_relative(self, path: Union[str, Path]) -> str:  # pragma: no cover
        if not isinstance(path, Path):
            path = Path(path)

        if not path.is_absolute():
            return str(path)

        return str(path.relative_to(self.path))

    def make_from_function(
        self,
        function: FuncType,
        ext: str = '.py',
        name: Optional[Union[str, Path]] = None,
        **env: Any,
    ) -> None:
        source = get_source_from_function(function, **env)

        if name:
            self.makefile(ext, **{self._make_relative(name): source})
        else:
            self.makefile(ext, source)

    def copy_pkg(self, clean: bool = True) -> None:
        path = self.path / 'prisma'
        copy_tree(BASE_PACKAGE_DIR, path)

        if clean:  # pragma: no branch
            result = self.runpython_c('import prisma_cleanup; prisma_cleanup.cleanup()')
            assert result.ret == 0

    def generate(
        self, schema: Optional[str] = None, options: str = '', **extra: Any
    ) -> 'subprocess.CompletedProcess[bytes]':
        path = self.make_schema(schema, options, **extra)
        args = [sys.executable, '-m', 'prisma', 'generate', f'--schema={path}']
        proc = subprocess.run(
            args,
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(str(proc.stdout, sys.getdefaultencoding()), file=sys.stdout)
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, args, proc.stdout, proc.stderr)

        return proc

    def make_schema(
        self,
        schema: Optional[str] = None,
        options: str = '',
        output: Optional[str] = None,
        **extra: Any,
    ) -> Path:
        if schema is None:
            schema = self.default_schema

        if output is None:  # pragma: no branch
            output = 'prisma'

        path = self.path.joinpath('schema.prisma')
        path.write_text(
            schema.format(
                output=escape_path(self.path.joinpath(output)),
                options=options,
                **extra,
            )
        )
        return path

    def makefile(self, ext: str, *args: str, **kwargs: str) -> None:
        self.pytester.makefile(ext, *args, **kwargs)

    def runpytest(self, *args: Union[str, 'os.PathLike[str]'], **kwargs: Any) -> 'RunResult':
        # pytest-sugar breaks result parsing
        return self.pytester.runpytest('-p', 'no:sugar', *args, **kwargs)

    def runpython_c(self, command: str) -> 'RunResult':
        return self.pytester.runpython_c(command)

    @contextlib.contextmanager
    def redirect_stdout_to_file(
        self,
    ) -> Iterator[Path]:
        path = self.path.joinpath(f'stdout-{uuid.uuid4()}.txt')

        with path.open('w') as file:
            with contextlib.redirect_stdout(file):
                yield path

    @property
    def path(self) -> Path:
        return Path(self.pytester.path)

    @override
    def __repr__(self) -> str:  # pragma: no cover
        return str(self)

    @override
    def __str__(self) -> str:  # pragma: no cover
        return f'<Testdir {self.path} >'


def get_source_from_function(function: FuncType, **env: Any) -> str:
    lines = inspect.getsource(function).splitlines()[1:]

    # setup env after imports
    for index, line in enumerate(lines):
        if not line.lstrip(' ').startswith(('import', 'from')):
            start = index
            break
    else:
        start = 0

    lines = textwrap.dedent('\n'.join(lines)).splitlines()
    for name, value in env.items():
        if isinstance(value, str):  # pragma: no branch
            value = f"'{value}'"

        lines.insert(start, f'{name} = {value}')

    return IMPORT_RELOADER + '\n'.join(lines)


@contextlib.contextmanager
def set_config(config: _config.Config) -> Iterator[_config.Config]:
    proxy = cast(LazyProxy[_config.Config], _config.config)
    old = proxy.__get_proxied__()

    try:
        proxy.__set_proxied__(config)
        yield config
    finally:
        proxy.__set_proxied__(old)


def patch_method(
    patcher: 'MonkeyPatch',
    obj: object,
    attr: str,
    callback: Optional[Callable[..., Any]] = None,
) -> Callable[[], Optional[CapturedArgs]]:
    """Helper for patching functions that are incompatible with MonkeyPatch.setattr

    e.g. __init__ methods
    """
    # work around for pyright: https://github.com/microsoft/pyright/issues/2757
    captured = cast(Optional[CapturedArgs], None)

    def wrapper(*args: Any, **kwargs: Any) -> None:
        nonlocal captured
        captured = (args[1:], kwargs)

        if callback is not None:
            callback(real_meth, *args, **kwargs)

    real_meth = getattr(obj, attr)
    patcher.setattr(obj, attr, wrapper, raising=True)
    return lambda: captured


skipif_windows = pytest.mark.skipif(platform.name() == 'windows', reason='Test is disabled on windows')
