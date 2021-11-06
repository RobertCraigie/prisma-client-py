from pathlib import Path

import pytest
from prisma import Client, errors
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
