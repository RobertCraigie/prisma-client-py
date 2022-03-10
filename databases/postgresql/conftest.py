# TODO: this should be shared between all tests
import asyncio
import inspect
from pathlib import Path
from contextvars import ContextVar

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.amber import AmberSnapshotExtension

from prisma import Prisma, register
from prisma.utils import async_run, get_or_create_event_loop


client_ctx: ContextVar['Prisma'] = ContextVar('client_ctx', default=Prisma())
SNAPSHOT_DIR: str = '__snapshots__'


class CustomAmberExtension(AmberSnapshotExtension):
    @property
    def _dirname(self) -> str:
        # share snapshots between database tests as they should all be the same
        # if there are database specific snapshots then they can easily override this
        # on a test by test basis
        return str(
            Path(self.test_location.filepath).parent.parent / SNAPSHOT_DIR
        )


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.use_extension(CustomAmberExtension)


@pytest.fixture(name='client', scope='session')
async def client_fixture() -> Prisma:
    client = client_ctx.get()
    if not client.is_connected():
        await client.connect()

    await cleanup_client(client)
    return client


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    return get_or_create_event_loop()


@pytest.fixture(autouse=True, scope='session')
def register_client_fixture() -> None:
    register(client_ctx.get())


def pytest_runtest_setup(item: pytest.Function) -> None:
    client = client_ctx.get()
    if not client.is_connected():
        async_run(client.connect())

    async_run(cleanup_client(client))


async def cleanup_client(client: Prisma) -> None:
    for _, item in inspect.getmembers(client):
        if item.__class__.__name__.endswith('Actions'):
            await item.delete_many()
