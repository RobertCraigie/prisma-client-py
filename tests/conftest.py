# pylint: disable=global-statement
import asyncio
import inspect
from typing import Any
from contextvars import ContextVar

import pytest
import prisma
from prisma import Client
from prisma.cli import setup_logging

from .utils import async_run


client_ctx: ContextVar['Client'] = ContextVar('client_ctx', default=Client())
LOGGING_CONTEXT_MANAGER = None


@pytest.fixture(name='client', scope='session')
def client_fixture() -> prisma.Client:
    client = client_ctx.get()
    async_run(client.connect())
    async_run(cleanup_client(client))
    return client


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


# TODO: don't emulate the with statement
def pytest_sessionstart(session: pytest.Session) -> None:
    global LOGGING_CONTEXT_MANAGER
    LOGGING_CONTEXT_MANAGER = setup_logging(use_handler=False)
    LOGGING_CONTEXT_MANAGER.__enter__()  # pylint: disable=no-member


def pytest_sessionfinish(session: pytest.Session) -> None:
    if LOGGING_CONTEXT_MANAGER is not None:
        LOGGING_CONTEXT_MANAGER.__exit__(None, None, None)  # pylint: disable=no-member


def pytest_runtest_setup(item: pytest.Function) -> None:
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
    for _, item in inspect.getmembers(client):
        if item.__class__.__name__.endswith('Actions'):
            await item.delete_many()
