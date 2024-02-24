import warnings
from typing import TYPE_CHECKING, Any, Mapping
from pathlib import Path
from datetime import timedelta

import httpx
import pytest
from mock import AsyncMock
from pytest_mock import MockerFixture

from prisma import ENGINE_TYPE, SCHEMA_PATH, Prisma, errors, get_client
from prisma.types import HttpConfig
from prisma.testing import reset_client
from prisma.cli.prisma import run
from prisma.engine.http import HTTPEngine
from prisma.engine.errors import AlreadyConnectedError
from prisma.http_abstract import DEFAULT_CONFIG

from .utils import Testdir, patch_method

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.mark.asyncio
async def test_catches_not_connected() -> None:
    """Trying to make a query before connecting raises an error"""
    client = Prisma()
    with pytest.raises(errors.ClientNotConnectedError) as exc:
        await client.post.delete_many()

    assert 'connect()' in str(exc)


@pytest.mark.asyncio
async def test_create_many_invalid_provider(client: Prisma) -> None:
    """Trying to call create_many() fails as SQLite does not support it"""
    with pytest.raises(errors.UnsupportedDatabaseError) as exc:
        await client.user.create_many([{'name': 'Robert'}])

    assert exc.match(r'create_many\(\) is not supported by sqlite')


@pytest.mark.asyncio
async def test_datasource_overwriting(testdir: Testdir, client: Prisma) -> None:
    """Ensure the client can connect and query to a custom datasource"""
    # we have to do this messing with the schema so that we can run db push on the new database
    schema = Path(__file__).parent / 'data' / 'schema.prisma'
    testdir.path.joinpath('schema.prisma').write_text(schema.read_text().replace('"file:dev.db"', 'env("_PY_DB")'))
    run(['db', 'push', '--skip-generate'], env={'_PY_DB': 'file:./tmp.db'})

    other = Prisma(
        datasource={'url': 'file:./tmp.db'},
    )
    await other.connect(timeout=timedelta(seconds=1))

    user = await other.user.create({'name': 'Robert'})
    assert user.name == 'Robert'

    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_context_manager() -> None:
    """Client can be used as a context manager to connect and disconnect from the database"""
    client = Prisma()
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

        client = Prisma(auto_register=True)
        assert get_client() == client


def test_engine_type() -> None:
    """The exported ENGINE_TYPE enum matches the actual engine type"""
    assert ENGINE_TYPE.value == 'binary'


@pytest.mark.asyncio
async def test_connect_timeout(mocker: MockerFixture) -> None:
    """Setting the timeout on a client and a per-call basis works"""
    client = Prisma(connect_timeout=timedelta(seconds=7))
    mocked = mocker.patch.object(
        client._engine_class,
        'connect',
        new=AsyncMock(),
    )

    await client.connect()
    mocked.assert_called_once_with(
        timeout=timedelta(seconds=7),
        datasources=[client._make_sqlite_datasource()],
    )
    mocked.reset_mock()

    await client.connect(timeout=timedelta(seconds=5))
    mocked.assert_called_once_with(
        timeout=timedelta(seconds=5),
        datasources=[client._make_sqlite_datasource()],
    )


@pytest.mark.asyncio
async def test_custom_http_options(monkeypatch: 'MonkeyPatch') -> None:
    """Custom http options are passed to the HTTPX Client"""

    def mock___init__(real__init__: Any, *args: Any, **kwargs: Any) -> None:
        # pass to real __init__ method to ensure types passed will actually work at runtime
        real__init__(*args, **kwargs)

    getter = patch_method(monkeypatch, httpx.AsyncClient, '__init__', mock___init__)

    def mock_app(args: Mapping[str, object], data: object) -> object:
        ...

    async def _test(config: HttpConfig) -> None:
        client = Prisma(
            http=config,
        )
        engine = client._create_engine()  # pylint: disable=protected-access
        assert isinstance(engine, HTTPEngine)
        engine.session.open()
        await engine.session.close()

        captured = getter()
        assert captured is not None
        assert captured == ((), {**DEFAULT_CONFIG, **config})

    await _test({'timeout': 1})
    await _test({'timeout': httpx.Timeout(5, connect=10, read=30)})
    await _test({'max_redirects': 1, 'trust_env': True})
    await _test({'http1': True, 'http2': False})
    await _test(
        config={
            'timeout': 200,
            'http1': True,
            'http2': False,
            'limits': httpx.Limits(max_connections=10),
            'max_redirects': 2,
            'trust_env': False,
        },
    )

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        await _test({'app': mock_app})


def test_old_client_alias() -> None:
    """Ensure that Prisma can be imported from the root package under the Client alias"""
    from prisma import Client, Prisma

    assert Client == Prisma


def test_sqlite_url(client: Prisma) -> None:
    """Ensure that the default overriden SQLite URL uses the correct relative path

    https://github.com/RobertCraigie/prisma-client-py/issues/409
    """
    rootdir = Path(__file__).parent

    url = client._make_sqlite_url('file:dev.db')
    assert url == f'file:{SCHEMA_PATH.parent.joinpath("dev.db")}'

    url = client._make_sqlite_url('file:dev.db', relative_to=rootdir)
    assert url == f'file:{rootdir.joinpath("dev.db")}'

    url = client._make_sqlite_url('sqlite:../dev.db', relative_to=rootdir)
    assert url == f'file:{rootdir.parent.joinpath("dev.db")}'

    # already absolute paths are not updated
    url = client._make_sqlite_url(
        f'sqlite:{rootdir.parent.joinpath("foo.db").absolute()}',
        relative_to=rootdir,
    )
    assert url == f'sqlite:{rootdir.parent.joinpath("foo.db").absolute()}'

    # unknown prefixes are not updated
    url = client._make_sqlite_url('unknown:dev.db', relative_to=rootdir)
    assert url == 'unknown:dev.db'

    # prefixes being dropped without affecting file name
    url = client._make_sqlite_url('file:file.db')
    assert url == f'file:{SCHEMA_PATH.parent.joinpath("file.db")}'

    url = client._make_sqlite_url('sqlite:sqlite.db')
    assert url == f'file:{SCHEMA_PATH.parent.joinpath("sqlite.db")}'


@pytest.mark.asyncio
async def test_copy() -> None:
    """The Prisma._copy() method forwards all relevant properties"""
    client1 = Prisma(
        log_queries=True,
        datasource={
            'url': 'file:foo.db',
        },
        connect_timeout=timedelta(seconds=15),
        http={
            'trust_env': False,
        },
    )
    client2 = client1._copy()
    assert not client2.is_connected() is None
    assert client2._log_queries is True
    assert client2._datasource == {'url': 'file:foo.db'}
    assert client2._connect_timeout == timedelta(seconds=15)
    assert client2._http_config == {'trust_env': False}

    await client1.connect()
    assert client1.is_connected()
    client3 = client1._copy()
    assert client3.is_connected()


@pytest.mark.asyncio
async def test_copied_client_does_not_close_engine(client: Prisma) -> None:
    """Deleting a Prisma._copy()'d client does not cause the engine to be stopped"""
    copied = client._copy()
    assert copied.is_connected()
    assert client.is_connected()

    del copied

    assert client.is_connected()
    await client.user.count()  # ensure queries can still be executed


def test_is_registered(client: Prisma) -> None:
    """The Prisma.is_registered() method can be used both when the client is registered
    and when there is no client registered at all.
    """
    assert client.is_registered()

    other_client = Prisma()
    assert not other_client.is_registered()

    with reset_client():
        assert not client.is_registered()
        assert not other_client.is_registered()
