# pylint: disable=global-statement
import os
import sys
import asyncio
import inspect
from typing import List, Iterator, TYPE_CHECKING

import pytest

import prisma
from prisma import Client
from prisma.cli import setup_logging
from prisma.utils import get_or_create_event_loop

from .utils import Runner, Testdir


if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from _pytest.pytester import Testdir as PytestTestdir


pytest_plugins = ['pytester']
LOGGING_CONTEXT_MANAGER = setup_logging(use_handler=False)


prisma.register(Client())


@pytest.fixture(name='client', scope='session')
async def client_fixture() -> Client:
    client = prisma.get_client()
    await client.connect()
    await cleanup_client(client)
    return client


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
    LOGGING_CONTEXT_MANAGER.__enter__()  # pylint: disable=no-member


def pytest_sessionfinish(session: pytest.Session) -> None:
    if LOGGING_CONTEXT_MANAGER is not None:  # pragma: no branch
        LOGGING_CONTEXT_MANAGER.__exit__(None, None, None)  # pylint: disable=no-member


def pytest_collection_modifyitems(
    session: pytest.Session, config: 'Config', items: List[pytest.Item]
) -> None:
    items.sort(key=lambda item: item.__class__.__name__ == 'IntegrationTestItem')


@pytest.fixture(name='cleanup_client', autouse=True)
async def cleanup_client_fixture(request: 'FixtureRequest', client: Client) -> None:
    if not client.is_connected():  # pragma: no cover
        await client.connect()

    item = request.node
    if not isinstance(item, pytest.Item) or marked_persist_data(item):
        return

    await cleanup_client(client)


def marked_persist_data(item: pytest.Item) -> bool:
    for marker in item.iter_markers():
        if marker.name == 'persist_data':
            return True
    return False


async def cleanup_client(client: Client) -> None:
    async with client.batch_() as batcher:
        for _, item in inspect.getmembers(batcher):
            if item.__class__.__name__.endswith('Actions'):
                item.delete_many()
