import inspect
from typing import TYPE_CHECKING, Iterator

import pytest

import prisma
from prisma import Prisma

from ._utils import request_has_client

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest


@pytest.fixture(name='_cleanup_session', scope='session', autouse=True)
def cleanup_session() -> Iterator[None]:
    yield

    client = prisma.get_client()
    if client.is_connected():
        client.disconnect()


@pytest.fixture(name='client', scope='session')
def client_fixture() -> Prisma:
    client = prisma.get_client()
    if not client.is_connected():  # pragma: no cover
        client.connect()

    cleanup_client(client)
    return client


@pytest.fixture(name='setup_client', autouse=True)
def setup_client_fixture(request: 'FixtureRequest') -> None:
    if not request_has_client(request):
        return

    if request.node.get_closest_marker('persist_data') is not None:
        return

    client = prisma.get_client()
    if not client.is_connected():  # pragma: no cover
        client.connect()

    cleanup_client(client)


def cleanup_client(client: Prisma) -> None:
    with client.batch_() as batcher:
        for _, item in inspect.getmembers(batcher):
            if item.__class__.__name__.endswith('Actions'):
                item.delete_many()
