import os
import sys
import uuid
import inspect
import textwrap
import subprocess
import contextlib
from pathlib import Path
from datetime import datetime
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Optional,
    List,
    Tuple,
    Union,
    Iterator,
    TYPE_CHECKING,
    cast,
)

import py
import click
import pytest_asyncio  # type: ignore
from click.testing import CliRunner, Result

from prisma.cli import main
from prisma._types import FuncType


if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.fixtures import FixtureFunctionMarker, _Scope
    from _pytest.monkeypatch import MonkeyPatch
    from _pytest.pytester import RunResult, Testdir as PytestTestdir


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

SCHEMA_HEADER = """
datasource db {{
  provider = "sqlite"
  url      = "file:dev.db"
}}

generator db {{
  provider = "coverage run -m prisma"
  output = "{output}"
  {options}
}}

"""

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
        self.default_cli = None  # type: Optional[click.Command]
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

        def _patched_subprocess_run(
            *args: Any, **kwargs: Any
        ) -> 'subprocess.CompletedProcess[str]':
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            kwargs['encoding'] = sys.getdefaultencoding()

            process = old_subprocess_run(*args, **kwargs)

            assert isinstance(process.stdout, str)

            print(process.stdout)
            print(process.stderr, file=sys.stderr)
            return process

        old_subprocess_run = subprocess.run
        self._patcher.setattr(
            subprocess, 'run', _patched_subprocess_run, raising=True
        )


class Testdir:
    __test__ = False
    SCHEMA_HEADER = SCHEMA_HEADER
    default_schema = DEFAULT_SCHEMA

    def __init__(self, testdir: 'PytestTestdir') -> None:
        self.testdir = testdir

    def _make_relative(
        self, path: Union[str, Path]
    ) -> str:  # pragma: no cover
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
            raise subprocess.CalledProcessError(
                proc.returncode, args, proc.stdout, proc.stderr
            )

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
        self.testdir.makefile(ext, *args, **kwargs)

    def runpytest(
        self, *args: Union[str, 'os.PathLike[str]'], **kwargs: Any
    ) -> 'RunResult':
        # pytest-sugar breaks result parsing
        return self.testdir.runpytest('-p', 'no:sugar', *args, **kwargs)

    @contextlib.contextmanager
    def redirect_stdout_to_file(
        self,
    ) -> Iterator[Path]:
        path = self.path.joinpath(f'stdout-{uuid.uuid4()}.txt')

        with path.open('w') as file:
            with contextlib.redirect_stdout(file):
                yield path

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
        if isinstance(value, str):  # pragma: no branch
            value = f"'{value}'"

        lines.insert(start, f'{name} = {value}')

    return IMPORT_RELOADER + '\n'.join(lines)


def assert_similar_time(
    dt1: datetime, dt2: datetime, threshold: float = 0.5
) -> None:
    """Assert the delta between the two datetimes is less than the given threshold (in seconds).

    This is required as there seems to be small data loss when marshalling and unmarshalling
    datetimes, for example:

    2021-09-26T15:00:18.708000+00:00 -> 2021-09-26T15:00:18.708776+00:00

    This issue does not appear to be solvable by us, please create an issue if you know of a solution.
    """
    if dt1 > dt2:
        delta = dt1 - dt2
    else:
        delta = dt2 - dt1

    assert delta.days == 0
    assert delta.total_seconds() < threshold


def assert_time_like_now(dt: datetime, threshold: int = 10) -> None:
    # NOTE: I do not know if prisma datetimes are always in UTC
    #
    # have to remove the timezone details as utcnow() is not timezone aware
    # and we cannot subtract a timezone aware datetime from a non timezone aware datetime
    dt = dt.replace(tzinfo=None)
    delta = datetime.utcnow() - dt
    assert delta.days == 0
    assert delta.total_seconds() < threshold


def escape_path(path: Union[str, Path]) -> str:
    if isinstance(path, Path):  # pragma: no branch
        path = str(path.absolute())

    return path.replace('\\', '\\\\')


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


def async_fixture(
    scope: 'Union[_Scope, Callable[[str, Config], _Scope]]' = 'function',
    params: Optional[Iterable[object]] = None,
    autouse: bool = False,
    ids: Optional[
        Union[
            Iterable[Union[None, str, float, int, bool]],
            Callable[[Any], Optional[object]],
        ]
    ] = None,
    name: Optional[str] = None,
) -> 'FixtureFunctionMarker':
    """Wrapper over pytest_asyncio.fixture providing type hints"""
    return cast(
        'FixtureFunctionMarker',
        pytest_asyncio.fixture(
            None,
            scope=scope,
            params=params,
            autouse=autouse,
            ids=ids,
            name=name,
        ),
    )
