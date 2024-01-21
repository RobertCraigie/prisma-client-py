from __future__ import annotations

import re
import sys
import subprocess
from typing import Any, List, Callable, Iterator, Optional
from pathlib import Path
from typing_extensions import override

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.single_file import SingleFileSnapshotExtension
from syrupy.extensions.amber.serializer import DataSerializer

from prisma.generator import BASE_PACKAGE_DIR
from prisma.generator.utils import remove_suffix

from .utils import ROOTDIR
from ...utils import skipif_windows


class OSAgnosticSingleFileExtension(SingleFileSnapshotExtension):
    # syrupy's types are only written to target mypy, as such
    # pyright does not understand them and reports them as unknown.
    # As this method is only called internally it is safe to type as Any
    @override
    def serialize(
        self,
        data: Any,
        *,
        exclude: Optional[Any] = None,
        matcher: Optional[Any] = None,
    ) -> bytes:
        serialized = DataSerializer.serialize(data, exclude=exclude, matcher=matcher)
        return bytes(serialized, 'utf-8')

    # we disable diffs as we don't really care what the diff is
    # we just care that there is a diff and it can take a very
    # long time for syrupy to calculate the diff
    # https://github.com/tophat/syrupy/issues/581
    @override
    def diff_snapshots(self, serialized_data: Any, snapshot_data: Any) -> str:
        return 'diff-is-disabled'  # pragma: no cover

    @override
    def diff_lines(self, serialized_data: Any, snapshot_data: Any) -> Iterator[str]:
        yield 'diff-is-disabled'  # pragma: no cover


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.use_extension(OSAgnosticSingleFileExtension)


def _clean_line(proc: 'subprocess.CompletedProcess[bytes]') -> str:
    return proc.stdout.decode('utf-8').rstrip('\n').rstrip('\r')


def get_files_from_templates(directory: Path) -> List[str]:
    """Return a list of all auto-generated python modules"""
    files: List[str] = []

    for template in directory.iterdir():
        if template.is_dir():
            files.extend(get_files_from_templates(template))
        elif template.name.endswith('.py.jinja') and not template.name.startswith('_'):
            if directory.name == 'templates':
                name = template.name
            else:
                name = str(template.relative_to(template.parent.parent))

            files.append(remove_suffix(name, '.jinja').replace('\\', '/'))

    return files


SYNC_ROOTDIR = ROOTDIR / '__prisma_sync_output__' / 'prisma'
ASYNC_ROOTDIR = ROOTDIR / '__prisma_async_output__' / 'prisma'
FILES = get_files_from_templates(BASE_PACKAGE_DIR / 'generator' / 'templates')
THIS_DIR = Path(__file__).parent
BINARY_PATH_RE = re.compile(r'BINARY_PATHS = (.*)')


def path_replacer(
    schema_path: Path,
) -> Callable[[object, object], Optional[object]]:
    def pathlib_matcher(data: object, path: object) -> Optional[object]:
        if not isinstance(data, str):  # pragma: no cover
            raise RuntimeError(f'schema_path_matcher expected data to be a `str` but received {type(data)} instead.')

        data = data.replace(
            f"Path('{schema_path.absolute().as_posix()}')",
            "Path('<absolute-schema-path>')",
        )
        data = BINARY_PATH_RE.sub("BINARY_PATHS = '<binary-paths-removed>'", data)
        return data

    return pathlib_matcher


# TODO: support running snapshot tests on windows


@skipif_windows
@pytest.mark.parametrize('file', FILES)
def test_sync(snapshot: SnapshotAssertion, file: str) -> None:
    """Ensure synchronous client files match"""
    assert SYNC_ROOTDIR.joinpath(file).absolute().read_text() == snapshot(
        matcher=path_replacer(THIS_DIR / 'sync.schema.prisma')  # type: ignore
    )


@skipif_windows
@pytest.mark.parametrize('file', FILES)
def test_async(snapshot: SnapshotAssertion, file: str) -> None:
    """Ensure asynchronous client files match"""
    assert ASYNC_ROOTDIR.joinpath(file).absolute().read_text() == snapshot(
        matcher=path_replacer(THIS_DIR / 'async.schema.prisma')  # type: ignore
    )


def test_sync_client_can_be_imported() -> None:
    """Synchronous client can be imported"""
    proc = subprocess.run(
        [sys.executable, '-c', 'import prisma; print(prisma.__file__)'],
        cwd=str(SYNC_ROOTDIR.parent),
        check=True,
        stdout=subprocess.PIPE,
    )
    assert _clean_line(proc) == str(SYNC_ROOTDIR / '__init__.py')


def test_async_client_can_be_imported() -> None:
    """Asynchronous client can be imported"""
    proc = subprocess.run(
        [sys.executable, '-c', 'import prisma; print(prisma.__file__)'],
        cwd=str(ASYNC_ROOTDIR.parent),
        check=True,
        stdout=subprocess.PIPE,
    )
    assert _clean_line(proc) == str(ASYNC_ROOTDIR / '__init__.py')
