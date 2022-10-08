import os
import sys
import asyncio
import inspect
from pathlib import Path
from typing import List, Iterator, TYPE_CHECKING

import pytest

import prisma
from prisma import Prisma
from prisma.cli import setup_logging
from prisma.testing import reset_client
from prisma.utils import get_or_create_event_loop

from .utils import Runner, Testdir, async_fixture


if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from _pytest.pytester import Testdir as PytestTestdir


pytest_plugins = ['pytester']
HOME_DIR = Path.home()
LOGGING_CONTEXT_MANAGER = setup_logging(use_handler=False)


prisma.register(Prisma())


@async_fixture(name='client', scope='session')
async def client_fixture() -> Prisma:
    client = prisma.get_client()
    if not client.is_connected():  # pragma: no cover
        await client.connect()

    await cleanup_client(client)
    return client


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: 'MonkeyPatch') -> None:
    # Set a custom home directory to use for caching binaries so that
    # when we make use of pytest's temporary directory functionality the binaries
    # don't have to be downloaded again.
    monkeypatch.setenv('PRISMA_HOME_DIR', str(HOME_DIR))


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    return get_or_create_event_loop()


@pytest.fixture()
def runner(monkeypatch: 'MonkeyPatch') -> Runner:
    """Fixture for running cli tests"""
    return Runner(patcher=monkeypatch)


@pytest.fixture(name='testdir')
def testdir_fixture(testdir: 'PytestTestdir') -> Iterator[Testdir]:
    cwd = os.getcwd()
    os.chdir(testdir.tmpdir)
    sys.path.insert(0, str(testdir.tmpdir))

    yield Testdir(testdir)

    os.chdir(cwd)
    sys.path.remove(str(testdir.tmpdir))


# TODO: don't emulate the with statement
def pytest_sessionstart(session: pytest.Session) -> None:
    LOGGING_CONTEXT_MANAGER.__enter__()


def pytest_sessionfinish(session: pytest.Session) -> None:
    if LOGGING_CONTEXT_MANAGER is not None:  # pragma: no branch
        LOGGING_CONTEXT_MANAGER.__exit__(None, None, None)


def pytest_collection_modifyitems(
    session: pytest.Session, config: 'Config', items: List[pytest.Item]
) -> None:
    items.sort(
        key=lambda item: item.__class__.__name__ == 'IntegrationTestItem'
    )


@pytest.fixture(name='patch_prisma', autouse=True)
def patch_prisma_fixture(request: 'FixtureRequest') -> Iterator[None]:
    if request_has_client(request):
        yield
    else:

        def _disable_access() -> None:
            raise RuntimeError(
                'Tests that access the prisma client must be decorated with: '
                '@pytest.mark.prisma'
            )

        with reset_client(_disable_access):  # type: ignore
            yield


@async_fixture(name='setup_client', autouse=True)
async def setup_client_fixture(request: 'FixtureRequest') -> None:
    if not request_has_client(request):
        return

    item = request.node
    if item.get_closest_marker('persist_data') is not None:
        return

    client = prisma.get_client()
    if not client.is_connected():  # pragma: no cover
        await client.connect()

    await cleanup_client(client)


def request_has_client(request: 'FixtureRequest') -> bool:
    """Return whether or not the current request uses the prisma client"""
    return (
        request.node.get_closest_marker('prisma') is not None
        or 'client' in request.fixturenames
    )


async def cleanup_client(client: Prisma) -> None:
    async with client.batch_() as batcher:
        for _, item in inspect.getmembers(batcher):
            if item.__class__.__name__.endswith('Actions'):
                item.delete_many()
