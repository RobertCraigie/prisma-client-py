from pathlib import Path
from typing import List, Any

import pytest
from syrupy import SnapshotAssertion
from syrupy.extensions.single_file import SingleFileSnapshotExtension

from prisma.generator import BASE_PACKAGE_DIR
from prisma.generator.utils import remove_suffix
from .utils import ROOTDIR


class SingleFileUTF8SnapshotExtension(SingleFileSnapshotExtension):
    def serialize(self, data: Any, **kwargs: Any) -> bytes:
        return bytes(data, 'utf8')


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.use_extension(SingleFileUTF8SnapshotExtension)


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

            files.append(remove_suffix(name, '.jinja'))

    return files


SYNC_ROOTDIR = ROOTDIR / '__prisma_sync_output__'
ASYNC_ROOTDIR = ROOTDIR / '__prisma_async_output__'
FILES = get_files_from_templates(BASE_PACKAGE_DIR / 'generator' / 'templates')


@pytest.mark.parametrize('file', FILES)
def test_sync(snapshot: SnapshotAssertion, file: str) -> None:
    assert SYNC_ROOTDIR.joinpath(file).absolute().read_text() == snapshot


@pytest.mark.parametrize('file', FILES)
def test_async(snapshot: SnapshotAssertion, file: str) -> None:
    assert ASYNC_ROOTDIR.joinpath(file).absolute().read_text() == snapshot
