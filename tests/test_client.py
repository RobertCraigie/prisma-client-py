from pathlib import Path

import pytest
from prisma import ENGINE_TYPE, Client, get_client, errors, engine
from prisma.testing import reset_client
from prisma.cli.prisma import run

from .utils import Testdir


@pytest.mark.asyncio
async def test_catches_not_connected() -> None:
    """Trying to make a query before connecting raises an error"""
    client = Client()
    with pytest.raises(errors.ClientNotConnectedError) as exc:
        await client.post.delete_many()

    assert 'connect()' in str(exc)


@pytest.mark.asyncio
async def test_create_many_invalid_provider(client: Client) -> None:
    """Trying to call create_many() fails as SQLite does not support it"""
    with pytest.raises(errors.UnsupportedDatabaseError) as exc:
        await client.user.create_many([{'name': 'Robert'}])

    assert exc.match(r'create_many\(\) is not supported by sqlite')


@pytest.mark.asyncio
async def test_datasource_overwriting(testdir: Testdir, client: Client) -> None:
    """Ensure the client can connect and query to a custom datasource"""
    # we have to do this messing with the schema so that we can run db push on the new database
    schema = Path(__file__).parent / 'data' / 'schema.prisma'
    testdir.path.joinpath('schema.prisma').write_text(
        schema.read_text().replace('"file:dev.db"', 'env("_PY_DB")')
    )
    run(['db', 'push', '--skip-generate'], env={'_PY_DB': 'file:./tmp.db'})

    other = Client(
        datasource={'url': 'file:./tmp.db'},
    )
    await other.connect(timeout=1)

    user = await other.user.create({'name': 'Robert'})
    assert user.name == 'Robert'

    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_context_manager() -> None:
    """Client can be used as a context manager to connect and disconnect from the database"""
    client = Client()
    assert not client.is_connected()

    async with client:
        assert client.is_connected()

    assert not client.is_connected()

    # ensure exceptions are propagated
    with pytest.raises(engine.errors.AlreadyConnectedError):
        async with client:
            assert client.is_connected()
            await client.connect()


def test_auto_register() -> None:
    """Client(auto_register=True) correctly registers the client instance"""
    with reset_client():
        with pytest.raises(errors.ClientNotRegisteredError):
            get_client()

        client = Client(auto_register=True)
        assert get_client() == client


def test_engine_type() -> None:
    """The exported ENGINE_TYPE enum matches the actual engine type"""
    assert ENGINE_TYPE.value == 'binary'
