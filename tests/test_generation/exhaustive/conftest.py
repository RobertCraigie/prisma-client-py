import shutil
from pathlib import Path

import pytest
from prisma.cli import prisma
from prisma.cli.utils import maybe_exit
from prisma.utils import DEBUG_GENERATOR

from .utils import ROOTDIR


def remove_generated_clients() -> None:
    output = ROOTDIR.joinpath('__prisma_sync_output__')
    if output.exists():
        shutil.rmtree(str(output))

    output = ROOTDIR.joinpath('__prisma_async_output__')
    if output.exists():
        shutil.rmtree(str(output))


def pytest_sessionstart(session: pytest.Session) -> None:
    """Cleanup output files on session start as these are cached in between test runs"""
    remove_generated_clients()


def pytest_sessionfinish(session: pytest.Session) -> None:
    if not DEBUG_GENERATOR:
        remove_generated_clients()


@pytest.fixture(autouse=True, scope='session')
def generate_clients() -> None:
    """Generate the clients required to run these tests"""
    base = Path(__file__).parent
    for schema in ['sync.schema.prisma', 'async.schema.prisma']:
        maybe_exit(prisma.run(['generate', f'--schema={base.joinpath(schema)}']))
