# pylint: disable=global-statement
import os
import sys
import asyncio
import inspect
from typing import Any, Iterator, TYPE_CHECKING
from contextvars import ContextVar

import pytest

import prisma
from prisma import Client
from prisma.cli import setup_logging

from . import contexts
from .utils import async_run, Runner, Testdir


if TYPE_CHECKING:
    from _pytest.pytester import Testdir as PytestTestdir


pytest_plugins = ['pytester']
client_ctx: ContextVar['Client'] = ContextVar('client_ctx', default=Client())
LOGGING_CONTEXT_MANAGER = setup_logging(use_handler=False)


@pytest.fixture(name='client', scope='session')
def client_fixture() -> prisma.Client:
    client = client_ctx.get()
    async_run(client.connect())
    async_run(cleanup_client(client))
    return client


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.fixture()
def runner() -> Runner:
    """Fixture for running cli tests"""
    return Runner()


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
    if LOGGING_CONTEXT_MANAGER is not None:
        LOGGING_CONTEXT_MANAGER.__exit__(None, None, None)  # pylint: disable=no-member


def pytest_runtest_setup(item: pytest.Function) -> None:
    contexts.clear()

    if not has_client_fixture(item) or marked_persist_data(item):
        return

    client = client_ctx.get()
    if client.is_connected():
        async_run(cleanup_client(client))


def has_client_fixture(item: Any) -> bool:
    # TODO: more strict check
    return hasattr(item, 'fixturenames') and 'client' in item.fixturenames


def marked_persist_data(item: pytest.Function) -> bool:
    for marker in item.iter_markers():
        if marker.name == 'persist_data':
            return True
    return False


async def cleanup_client(client: Client) -> None:
    async with client.batch_() as batcher:
        for _, item in inspect.getmembers(batcher):
            if item.__class__.__name__.endswith('Actions'):
                item.delete_many()
