import os
import sys
import inspect
import asyncio
import textwrap
import subprocess
import contextlib
from pathlib import Path
from datetime import datetime
from typing import (
    Coroutine,
    Any,
    Optional,
    List,
    Dict,
    Union,
    Iterator,
    cast,
    TYPE_CHECKING,
)

import py
import click
import pkg_resources
from click.testing import CliRunner, Result
from pkg_resources import EntryPoint, Distribution

from prisma.cli import main
from prisma._types import FuncType


if TYPE_CHECKING:
    from _pytest.pytester import RunResult, Testdir as PytestTestdir


# as we are generating new modules we need to clear them from
# the module cache so that python actually picks them up
# when we import them again, however we also have to ignore
# any prisma.generator modules as we rely on the import caching
# mechanism for loading partial model types
IMPORT_RELOADER = '''
import sys
for name in sys.modules.copy():
    if 'prisma' in name and 'generator' not in name:
        sys.modules.pop(name, None)
'''

DEFAULT_SCHEMA = '''
datasource db {{
  provider = "sqlite"
  url      = "file:dev.db"
}}

generator db {{
  provider = "coverage run -m prisma"
  output = "{output}"
  {options}
}}

model User {{
  id           String   @id @default(cuid())
  created_at   DateTime @default(now())
  updated_at   DateTime @updatedAt
  name         String
}}
'''


class Runner:
    def __init__(self) -> None:
        self._runner = CliRunner()
        self.default_cli = None  # type: Optional[click.Command]

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

            @click.command()
            def cli() -> None:  # pylint: disable=function-redefined
                if args is not None:
                    # fake invocation context
                    args.insert(0, 'prisma')

                main(args, use_handler=False, do_cleanup=False, pipe=True)

            # mypy doesn't pick up the def properly
            cli = cast(click.Command, cli)

            # we don't pass any args to click as we need to parse them ourselves
            default_args = []

        with temp_env_update({'_PRISMA_PY_SHOULD_PIPE': '1'}):
            return self._runner.invoke(cli, default_args, **kwargs)


class Testdir:
    __test__ = False
    default_schema = DEFAULT_SCHEMA

    def __init__(self, testdir: 'PytestTestdir') -> None:
        self.testdir = testdir

    def _make_relative(self, path: Union[str, Path]) -> str:
        if not isinstance(path, Path):
            path = Path(path)

        if not path.is_absolute():
            return str(path)

        return str(path.relative_to(self.path))

    def _resolve_name(self, func: FuncType, name: Optional[str] = None) -> str:
        if name is None:
            return func.__name__

        return name

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

    def generate(
        self, schema: Optional[str] = None, options: str = '', **extra: Any
    ) -> None:
        path = self.make_schema(schema, options, **extra)
        args = [sys.executable, '-m', 'prisma', 'generate', f'--schema={path}']
        proc = subprocess.run(  # pylint: disable=subprocess-run-check
            args,
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(str(proc.stdout, 'utf-8'), file=sys.stdout)
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode, args, proc.stdout, proc.stderr
            )

    def make_schema(
        self,
        schema: Optional[str] = None,
        options: str = '',
        output: Optional[str] = None,
        **extra: Any,
    ) -> Path:
        if schema is None:
            schema = self.default_schema

        if output is None:
            output = 'prisma'

        path = self.path.joinpath('schema.prisma')
        path.write_text(
            schema.format(output=self.path.joinpath(output), options=options, **extra)
        )
        return path

    def makefile(self, ext: str, *args: str, **kwargs: str) -> None:
        self.testdir.makefile(ext, *args, **kwargs)

    def runpytest(
        self, *args: Union[str, 'os.PathLike[str]'], **kwargs: Any
    ) -> 'RunResult':
        return self.testdir.runpytest(*args, **kwargs)

    def create_module(
        self, func: FuncType, name: Optional[str] = None, mod: str = 'mod', **env: Any
    ) -> None:
        mod_path = self.path / mod
        mod_path.mkdir(exist_ok=True)
        mod_path.joinpath('__init__.py').touch()
        name = self._resolve_name(func, name)
        self.make_from_function(func, name=mod_path / name, **env)

    @contextlib.contextmanager
    def install_module(
        self,
        pkg: Optional[str] = None,
        install_flags: Optional[List[str]] = None,
        uninstall_flags: Optional[List[str]] = None,
    ) -> Iterator[None]:
        if install_flags is None:
            install_flags = ['-e', '.']

        if uninstall_flags is None:
            if pkg is None:  # pragma: no cover
                raise TypeError('Missing required argument: pkg')

            uninstall_flags = ['-y', pkg]

        try:
            subprocess.run(['pip', 'install', *install_flags], check=True)
            yield
        finally:
            subprocess.run(['pip', 'uninstall', *uninstall_flags], check=True)

    @contextlib.contextmanager
    def create_entry_point(
        self,
        func: FuncType,
        name: Optional[str] = None,
        mod: str = 'mod',
        clear: bool = True,
    ) -> Iterator[None]:
        name = self._resolve_name(func, name)
        self.create_module(func, name=name, mod=mod)

        entries = None

        try:
            entries = pkg_resources.get_distribution('prisma').get_entry_map()['prisma']

            if clear:
                # TODO: clear all entries, this curently only clears
                # entry points defined in the prisma package, other
                # packages prisma entry points are not cleared
                entries.clear()

            entries[name] = EntryPoint.parse(
                f'{name} = {mod}.{name}', dist=Distribution(mod)
            )
            yield
        finally:
            if entries is not None:
                entries.pop(name, None)

    @property
    def tmpdir(self) -> py.path.local:
        return self.testdir.tmpdir

    @property
    def path(self) -> Path:
        return Path(self.tmpdir)

    def __repr__(self) -> str:  # pragma: no cover
        return str(self)

    def __str__(self) -> str:  # pragma: no cover
        return f'<Testdir {self.tmpdir} >'


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
        if isinstance(value, str):
            value = f'\'{value}\''

        lines.insert(start, f'{name} = {value}')

    return IMPORT_RELOADER + '\n'.join(lines)


@contextlib.contextmanager
def temp_env_update(env: Dict[str, str]) -> Iterator[None]:
    try:
        old = os.environ.copy()
        os.environ.update(env)
        yield
    finally:
        for key in env.keys():
            os.environ.pop(key, None)

        os.environ.update(old)


def async_run(coro: Coroutine[Any, Any, Any]) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


def assert_time_like_now(dt: datetime, threshold: int = 10) -> None:
    # NOTE: I do not know if prisma datetimes are always in UTC
    #
    # have to remove the timezone details as utcnow() is not timezone aware
    # and we cannot subtract a timezone aware datetime from a non timezone aware datetime
    dt = dt.replace(tzinfo=None)
    delta = datetime.utcnow() - dt
    assert delta.days == 0
    assert delta.total_seconds() < threshold
