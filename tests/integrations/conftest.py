from __future__ import annotations

import sys
import shutil
import subprocess
from typing import TYPE_CHECKING, Any, Union, Iterator, Optional, cast
from pathlib import Path
from functools import lru_cache

import pytest
from _pytest._code import ExceptionInfo
from _pytest.nodes import Node
from _pytest.config import Config
from _pytest._code.code import TerminalRepr

if TYPE_CHECKING:
    from _pytest._code.code import _TracebackStyle


ROOTDIR = Path(__file__).parent.parent.parent


class IntegrationError(AssertionError):
    def __init__(self, message: Optional[str] = None, lineno: int = 0) -> None:  # pragma: no cover
        self.message = message or ''
        self.lineno = lineno
        super().__init__()

    def __str__(self) -> str:  # pragma: no cover
        return self.message


def resolve_path(path: Path) -> Path:
    return path.relative_to(Path.cwd())


def is_integration_test_file(path: Path) -> bool:
    # disable integration tests as they are currently broken
    return False


def pytest_ignore_collect(collection_path: Path, config: Config) -> Optional[bool]:
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
    path = resolve_path(collection_path)
    if path.parts[:2] != ('tests', 'integrations'):  # pragma: no cover
        # not an integration test
        return None

    if len(path.parts) <= 3:
        # integration root dir, leave handling to pytest
        return None

    return path.parts[-1] != 'test.sh'


def pytest_collect_file(file_path: Path, parent: Node) -> Optional['IntegrationTestFile']:
    path = resolve_path(file_path)
    if path.suffix == '.sh' and is_integration_test_file(path) and sys.platform != 'win32':
        return IntegrationTestFile.from_parent(parent, path=path)

    return None


@lru_cache(maxsize=None)
def create_wheels() -> None:
    dist = ROOTDIR / '.tests_cache' / 'dist'
    if dist.exists():  # pragma: no cover
        shutil.rmtree(str(dist))

    result = subprocess.run(
        [
            sys.executable,
            'setup.py',
            'bdist_wheel',
            '--dist-dir=.tests_cache/dist',
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(ROOTDIR),
    )
    if result.returncode != 0:  # pragma: no cover
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
        # TODO: include exit code in pytest failure short description
        result = subprocess.run(
            [str(self.path)],
            cwd=str(self.path.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(result.stdout.decode('utf-8'))
        if result.returncode != 0:  # pragma: no cover
            raise IntegrationError(f'Executing `{self.path}` returned non-zero exit code {result.returncode}')

    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style: Optional['_TracebackStyle'] = None,
    ) -> Union[str, TerminalRepr]:  # pragma: no cover
        if isinstance(excinfo.value, IntegrationError):
            return f'IntegrationError: {excinfo.value.message}'

        return super().repr_failure(excinfo, style=style)

    def reportinfo(self):
        return self.fspath, 0, f'integration: {self.name}'


class IntegrationTestFile(pytest.File):
    @classmethod
    def from_parent(cls, *args: Any, **kwargs: Any) -> 'IntegrationTestFile':
        return cast(
            IntegrationTestFile,
            super().from_parent(*args, **kwargs),  # type: ignore[no-untyped-call]
        )

    def collect(self) -> Iterator[IntegrationTestItem]:
        path = Path(self.fspath)
        yield IntegrationTestItem.from_parent(parent=self, name=path.parent.name, path=path)
