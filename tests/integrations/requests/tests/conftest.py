import inspect
from contextvars import ContextVar

import pytest
from prisma import Client


client_ctx: ContextVar[Client] = ContextVar('client_ctx', default=Client())


@pytest.fixture(name='client', scope='session')
def client_fixture() -> Client:
    client = client_ctx.get()
    client.connect()
    cleanup_client(client)
    return client


def pytest_runtest_setup(item: pytest.Function) -> None:
    client = client_ctx.get()
    if client.is_connected():
        cleanup_client(client)


def cleanup_client(client: Client) -> None:
    for _, item in inspect.getmembers(client):
        if item.__class__.__name__.endswith('Actions'):
            item.delete_many()
