from pathlib import Path
from typing import TYPE_CHECKING, Mapping, Optional, Tuple, cast

import httpx
import pytest
from mock import AsyncMock
from pytest_mock import MockerFixture
from prisma import ENGINE_TYPE, Client, get_client, errors
from prisma.engine.http import HTTPEngine
from prisma.engine.errors import AlreadyConnectedError
from prisma.testing import reset_client
from prisma.cli.prisma import run
from prisma.types import HttpConfig

from .utils import Testdir


if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


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
    with pytest.raises(AlreadyConnectedError):
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


@pytest.mark.asyncio
async def test_connect_timeout(mocker: MockerFixture) -> None:
    """Setting the timeout on a client and a per-call basis works"""
    client = Client(connect_timeout=7)
    mocked = mocker.patch.object(
        client._engine_class,  # pylint: disable=protected-access
        'connect',
        new=AsyncMock(),
    )

    await client.connect()
    mocked.assert_called_once_with(timeout=7, datasources=None)
    mocked.reset_mock()

    await client.connect(timeout=5)
    mocked.assert_called_once_with(timeout=5, datasources=None)


@pytest.mark.asyncio
async def test_custom_http_options(monkeypatch: 'MonkeyPatch') -> None:
    """Custom http options are passed to the HTTPX Client"""

    # work around for a bug in pyright: https://github.com/microsoft/pyright/issues/2757
    captured = cast(Optional[Tuple[Tuple[object, ...], Mapping[str, object]]], None)

    # TODO: extract this
    # can't use mocker as init methods must return None and mocker requires returning a value
    def mock___init__(self: httpx.AsyncClient, *args: object, **kwargs: object) -> None:
        nonlocal captured
        captured = (args, kwargs)

        # pass to real __init__ method to ensure types passed will actually work at runtime
        # TODO: ensure passed types match type hints
        real___init__(self, *args, **kwargs)

    real___init__ = httpx.AsyncClient.__init__
    monkeypatch.setattr(httpx.AsyncClient, '__init__', mock___init__, raising=True)

    def mock_app(args: Mapping[str, object], data: object) -> object:
        ...

    async def _test(config: HttpConfig) -> None:
        client = Client(
            http=config,
        )
        engine = client._create_engine()  # pylint: disable=protected-access
        assert isinstance(engine, HTTPEngine)
        engine.session.open()
        await engine.session.close()

        assert captured is not None
        assert captured == ((), config)

    await _test({'timeout': 1})
    await _test({'timeout': httpx.Timeout(5, connect=10, read=30)})
    await _test({'max_redirects': 1, 'trust_env': True})
    await _test({'http1': True, 'http2': False})
    await _test(
        config={
            'app': mock_app,
            'timeout': 200,
            'http1': True,
            'http2': False,
            'limits': httpx.Limits(max_connections=10),
            'max_redirects': 2,
            'trust_env': False,
        },
    )
