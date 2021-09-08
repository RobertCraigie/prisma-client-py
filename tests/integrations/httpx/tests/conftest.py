import inspect

import pytest
from prisma import Client


@pytest.fixture(name='client', scope='session')
def client_fixture() -> Client:
    client = Client()
    client.connect()
    return client


@pytest.fixture(autouse=True)
def cleanup_client(client: Client) -> None:
    for _, item in inspect.getmembers(client):
        if item.__class__.__name__.endswith('Actions'):
            item.delete_many()
