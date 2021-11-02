import inspect

import pytest
import prisma
from prisma import Client, register, get_client


def pytest_sessionstart(session: pytest.Session) -> None:
    # we need to register the client here as this conftest is imported
    # by pytest multiple times
    try:
        register(Client())
    except prisma.errors.ClientAlreadyRegisteredError:
        pass


@pytest.fixture(name='client', scope='session')
def client_fixture() -> Client:
    client = get_client()
    client.connect()
    return client


@pytest.fixture(autouse=True)
def cleanup_client(client: Client) -> None:
    for _, item in inspect.getmembers(client):
        if item.__class__.__name__.endswith('Actions'):
            item.delete_many()
