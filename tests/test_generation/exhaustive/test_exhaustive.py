import sys
import subprocess
from pathlib import Path
from typing import Any, List, Optional

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.amber.serializer import DataSerializer
from syrupy.extensions.single_file import SingleFileSnapshotExtension

from prisma.generator import BASE_PACKAGE_DIR
from prisma.generator.utils import remove_suffix
from .utils import ROOTDIR


class OSAgnosticSingleFileExtension(SingleFileSnapshotExtension):

    # syrupy's types are only written to target mypy, as such
    # pyright does not understand them and reports them as unknown.
    # As this method is only called internally it is safe to type as Any
    def serialize(
        self,
        data: Any,
        *,
        exclude: Optional[Any] = None,
        matcher: Optional[Any] = None,
    ) -> bytes:
        serialized = DataSerializer.serialize(
            data, exclude=exclude, matcher=matcher
        )
        return bytes(serialized, 'utf-8')


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
        elif template.name.endswith(
            '.py.jinja'
        ) and not template.name.startswith('_'):
            if directory.name == 'templates':
                name = template.name
            else:
                name = str(template.relative_to(template.parent.parent))

            files.append(remove_suffix(name, '.jinja').replace('\\', '/'))

    return files


SYNC_ROOTDIR = ROOTDIR / '__prisma_sync_output__' / 'prisma'
ASYNC_ROOTDIR = ROOTDIR / '__prisma_async_output__' / 'prisma'
FILES = get_files_from_templates(BASE_PACKAGE_DIR / 'generator' / 'templates')


@pytest.mark.parametrize('file', FILES)
def test_sync(snapshot: SnapshotAssertion, file: str) -> None:
    """Ensure synchronous client files match"""
    assert SYNC_ROOTDIR.joinpath(file).absolute().read_text() == snapshot


@pytest.mark.parametrize('file', FILES)
def test_async(snapshot: SnapshotAssertion, file: str) -> None:
    """Ensure asynchronous client files match"""
    assert ASYNC_ROOTDIR.joinpath(file).absolute().read_text() == snapshot


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
