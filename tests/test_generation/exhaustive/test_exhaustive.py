import sys
import subprocess
from pathlib import Path
from typing import List

import pytest
from syrupy.assertion import SnapshotAssertion

from prisma.generator import BASE_PACKAGE_DIR
from prisma.generator.utils import remove_suffix
from .utils import ROOTDIR


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
    assert proc.stdout.decode('utf-8').rstrip('\n') == str(SYNC_ROOTDIR / '__init__.py')


def test_async_client_can_be_imported() -> None:
    """Asynchronous client can be imported"""
    proc = subprocess.run(
        [sys.executable, '-c', 'import prisma; print(prisma.__file__)'],
        cwd=str(ASYNC_ROOTDIR.parent),
        check=True,
        stdout=subprocess.PIPE,
    )
    assert proc.stdout.decode('utf-8').rstrip('\n') == str(
        ASYNC_ROOTDIR / '__init__.py'
    )
