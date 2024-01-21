import inspect

import pytest

import prisma
from prisma import Prisma, register, get_client


def pytest_sessionstart(session: pytest.Session) -> None:
    # we need to register the client here as this conftest is imported
    # by pytest multiple times
    try:
        register(Prisma())
    except prisma.errors.ClientAlreadyRegisteredError:  # pragma: no cover
        pass


@pytest.fixture(name='client', scope='session')
def client_fixture() -> Prisma:
    client = get_client()
    client.connect()
    return client


@pytest.fixture(autouse=True)
def cleanup_client(client: Prisma) -> None:
    for _, item in inspect.getmembers(client):
        if item.__class__.__name__.endswith('Actions'):
            item.delete_many()
