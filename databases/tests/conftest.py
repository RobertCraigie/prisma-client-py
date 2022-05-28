import os
import asyncio
import inspect
from typing import TYPE_CHECKING, Iterator

import pytest

import prisma
from prisma import Prisma
from prisma.testing import reset_client
from prisma.utils import get_or_create_event_loop

from .utils import RAW_QUERIES_MAPPING, RawQueries, async_fixture
from ..utils import DatabaseConfig


if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest


prisma.register(Prisma())


@async_fixture(name='client', scope='session')
async def client_fixture() -> Prisma:
    client = prisma.get_client()
    if not client.is_connected():  # pragma: no cover
        await client.connect()

    await cleanup_client(client)
    return client


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    return get_or_create_event_loop()


@pytest.fixture(name='patch_prisma', autouse=True)
def patch_prisma_fixture(request: 'FixtureRequest') -> Iterator[None]:
    if request_has_client(request):
        yield
    else:

        def _disable_access() -> None:
            raise RuntimeError(
                'Tests that access the prisma client must be decorated with: '
                '@pytest.mark.prisma'
            )

        with reset_client(_disable_access):  # type: ignore
            yield


@async_fixture(name='setup_client', autouse=True)
async def setup_client_fixture(request: 'FixtureRequest') -> None:
    if not request_has_client(request):
        return

    client = prisma.get_client()
    if not client.is_connected():  # pragma: no cover
        await client.connect()

    await cleanup_client(client)


# TODO: better error messages for invalid state
@pytest.fixture(name='datasource')
def datasource_fixture() -> str:
    return os.environ['PRISMA_DATABASE']


@pytest.fixture(name='raw_queries')
def raw_queries_fixture(datasource: str) -> RawQueries:
    return RAW_QUERIES_MAPPING[datasource]


@pytest.fixture(name='config', scope='session')
def config_fixture() -> DatabaseConfig:
    return DatabaseConfig.parse_raw(os.environ['DATABASE_CONFIG'])


def request_has_client(request: 'FixtureRequest') -> bool:
    """Return whether or not the current request uses the prisma client"""
    return (
        request.node.get_closest_marker('prisma') is not None
        or 'client' in request.fixturenames
    )


async def cleanup_client(client: Prisma) -> None:
    async with client.batch_() as batcher:
        for _, item in inspect.getmembers(batcher):
            if item.__class__.__name__.endswith('Actions'):
                item.delete_many()
