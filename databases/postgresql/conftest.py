# TODO: this should be shared between all tests
import asyncio
import inspect
from contextvars import ContextVar

import pytest

from prisma import Prisma, register
from prisma.utils import async_run, get_or_create_event_loop


client_ctx: ContextVar['Prisma'] = ContextVar('client_ctx', default=Prisma())


@pytest.fixture(name='client', scope='session')
def client_fixture() -> Prisma:
    client = client_ctx.get()
    async_run(client.connect())
    async_run(cleanup_client(client))
    return client


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    return get_or_create_event_loop()


@pytest.fixture(autouse=True, scope='session')
def register_client_fixture() -> None:
    register(client_ctx.get())


def pytest_runtest_setup(item: pytest.Function) -> None:
    client = client_ctx.get()
    if client.is_connected():
        async_run(cleanup_client(client))


async def cleanup_client(client: Prisma) -> None:
    for _, item in inspect.getmembers(client):
        if item.__class__.__name__.endswith('Actions'):
            await item.delete_many()
