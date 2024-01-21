import inspect
from typing import TYPE_CHECKING, AsyncIterator

import prisma
from prisma import Prisma
from lib.testing import async_fixture

from ._utils import request_has_client

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest


@async_fixture(name='_cleanup_session', scope='session', autouse=True)
async def cleanup_session() -> AsyncIterator[None]:
    yield

    client = prisma.get_client()
    if client.is_connected():
        await client.disconnect()


@async_fixture(name='client', scope='session')
async def client_fixture() -> Prisma:
    client = prisma.get_client()
    if not client.is_connected():  # pragma: no cover
        await client.connect()

    await cleanup_client(client)
    return client


@async_fixture(name='setup_client', autouse=True)
async def setup_client_fixture(request: 'FixtureRequest') -> None:
    if not request_has_client(request):
        return

    if request.node.get_closest_marker('persist_data') is not None:
        return

    client = prisma.get_client()
    if not client.is_connected():  # pragma: no cover
        await client.connect()

    await cleanup_client(client)


async def cleanup_client(client: Prisma) -> None:
    async with client.batch_() as batcher:
        for _, item in inspect.getmembers(batcher):
            if item.__class__.__name__.endswith('Actions'):
                item.delete_many()
