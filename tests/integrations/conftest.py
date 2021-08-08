import sys
import shutil
import subprocess
from pathlib import Path
from functools import lru_cache
from typing import Optional, Union, Iterator, cast, Any, TYPE_CHECKING

import pytest
from py._path.local import LocalPath

from _pytest.nodes import Node
from _pytest.config import Config
from _pytest._io import TerminalWriter
from _pytest._code import ExceptionInfo
from _pytest._code.code import TerminalRepr, ReprEntry, ReprFileLocation

if TYPE_CHECKING:
    from _pytest._code.code import _TracebackStyle


ROOTDIR = Path(__file__).parent.parent.parent


class TraceLastReprEntry(ReprEntry):
    def toterminal(self, tw: TerminalWriter) -> None:
        if not self.reprfileloc:
            return

        self.reprfileloc.toterminal(tw)
        for line in self.lines:
            red = line.startswith('E   ')
            tw.line(line, bold=True, red=red)

        return


class IntegrationError(AssertionError):
    def __init__(self, error_message: Optional[str] = None, lineno: int = 0) -> None:
        self.error_message = error_message or ''
        self.lineno = lineno
        super().__init__()

    def __str__(self) -> str:
        return self.error_message


def resolve_path(path: LocalPath) -> Path:
    return Path(path).relative_to(Path.cwd())


def is_integration_test_file(local_path: LocalPath) -> bool:
    path = resolve_path(local_path)
    if len(path.parts) != 4:
        return False

    return path.parts[:2] == ('tests', 'integrations') and path.parts[-1] == 'test.sh'


def pytest_ignore_collect(path: LocalPath, config: Config) -> Optional[bool]:
    """We need to ignore any integration test sub-paths

    For example we need to include

    tests/integrations
    tests/integrations/*
    tests/integrations/basic/test.sh

    but ignore anything that looks like

    tests/integrations/basic/*
    tests/integrations/basic/conftest.py
    tests/integrations/basic/tests/test_foo.py
    """
    pathlib_path = resolve_path(path)
    if pathlib_path.parts[:2] != ('tests', 'integrations'):
        # not an integration test
        return None

    if len(pathlib_path.parts) <= 3:
        # integration root dir, leave handling to pytest
        return None

    return pathlib_path.parts[-1] != 'test.sh'


def pytest_collect_file(
    path: LocalPath, parent: Node
) -> Optional['IntegrationTestFile']:
    if path.ext == '.sh' and is_integration_test_file(path):
        return IntegrationTestFile.from_parent(parent, fspath=path)

    return None


@lru_cache(maxsize=None)
def create_wheels() -> None:
    dist = ROOTDIR / '.tests_cache' / 'dist'
    if dist.exists():
        shutil.rmtree(str(dist))

    result = subprocess.run(
        [sys.executable, 'setup.py', 'bdist_wheel', '--dist-dir=.tests_cache/dist'],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(ROOTDIR),
    )
    if result.returncode != 0:
        print(result.stdout.decode('utf-8'))
        raise RuntimeError('Could not build wheels, see output above.')


class IntegrationTestItem(pytest.Item):
    def __init__(
        self,
        name: str,
        parent: Optional['IntegrationTestFile'] = None,
        config: Optional[Config] = None,
        *,
        path: Path,
    ) -> None:
        super().__init__(name, parent, config)
        self.path = path
        self.starting_lineno = 1

    def setup(self) -> None:
        create_wheels()

    def runtest(self) -> None:
        result = subprocess.run(
            [str(self.path)],
            cwd=str(self.path.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(result.stdout.decode('utf-8'))
        if result.returncode != 0:
            raise IntegrationError(
                f'Executing `{self.path}` returned non-zero exit code {result.returncode}'
            )

    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style: Optional['_TracebackStyle'] = None,
    ) -> Union[str, TerminalRepr]:
        """Remove unnecessary error traceback if applicable

        this method is taken directly from pytest-mypy-plugins along with
        related classes, e.g. TraceLastReprEntry
        """
        # NOTE: I do not know how much of this code is required / functioning as expected
        if excinfo.errisinstance(SystemExit):
            # We assume that before doing exit() (which raises SystemExit) we've printed
            # enough context about what happened so that a stack trace is not useful.
            return excinfo.exconly(tryshort=True)

        if excinfo.errisinstance(IntegrationError):
            # with traceback removed
            excinfo = cast(ExceptionInfo[IntegrationError], excinfo)
            exception_repr = excinfo.getrepr(style='short')
            exception_repr.reprcrash.message = ''  # type: ignore
            repr_file_location = (
                ReprFileLocation(  # pyright: reportGeneralTypeIssues=false
                    path=self.fspath,
                    lineno=self.starting_lineno + excinfo.value.lineno,
                    message='',
                )
            )
            repr_tb_entry = TraceLastReprEntry(
                exception_repr.reprtraceback.reprentries[-1].lines[1:],
                None,
                None,
                repr_file_location,
                'short',
            )
            exception_repr.reprtraceback.reprentries = [repr_tb_entry]
            return exception_repr

        return super().repr_failure(excinfo, style='native')


class IntegrationTestFile(pytest.File):
    @classmethod
    def from_parent(
        cls, *args: Any, **kwargs: Any
    ) -> 'IntegrationTestFile':  # pyright: reportIncompatibleMethodOverride=false
        return cast(
            IntegrationTestFile,
            super().from_parent(*args, **kwargs),  # type: ignore[no-untyped-call]
        )

    def collect(self) -> Iterator[IntegrationTestItem]:
        path = Path(self.fspath)
        yield IntegrationTestItem.from_parent(
            parent=self, name=path.parent.name, path=path
        )
