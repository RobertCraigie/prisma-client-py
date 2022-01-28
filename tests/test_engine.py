import asyncio
import contextlib
from pathlib import Path
from typing import Iterator, Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_subprocess import FakeProcess

from prisma import Client
from prisma.binaries import BINARIES, PLATFORM_EXE_EXTENSION
from prisma.binaries.binaries import (
    ENGINE_VERSION,
    ENGINES,
    InvalidBinaryVersion,
    PrismaSettings,
    engines_from_settings,
)
from prisma.engine import errors
from prisma.engine.query import QueryEngine
from prisma._compat import get_running_loop
from prisma.utils import temp_env_update

from .utils import Testdir


@contextlib.contextmanager
def no_event_loop() -> Iterator[None]:
    try:
        current: Optional[asyncio.AbstractEventLoop] = get_running_loop()
    except RuntimeError:
        current = None
    try:
        asyncio.set_event_loop(None)
        yield
    finally:
        asyncio.set_event_loop(current)


@pytest.mark.asyncio
async def test_engine_connects() -> None:
    """Can connect to engine"""
    db = Client()
    await db.connect()

    with pytest.raises(errors.AlreadyConnectedError):
        await db.connect()

    await db.disconnect()


def test_stopping_engine_on_closed_loop() -> None:
    """Stopping the engine with no event loop available does not raise an error"""
    with no_event_loop():
        engine = QueryEngine(dml='')
        engine.stop()


def test_engine_binary_does_not_exist(monkeypatch: MonkeyPatch) -> None:
    """No query engine binary found raises an error"""

    def mock_exists(path: Path) -> bool:
        return False

    monkeypatch.setattr(Path, 'exists', mock_exists, raising=True)

    with pytest.raises(FileNotFoundError) as exc:
        BINARIES[0].ensure_binary()

    assert exc.match(r'.* binary not found at .*\nTry running `prisma fetch`')


def test_mismatched_version_error(fake_process: FakeProcess) -> None:
    """Mismatched query engine versions raises an error"""
    query_engine = ENGINES[0]
    fake_process.register_subprocess(
        [str(query_engine.path), '--version'],
        stdout='query-engine unexpected-hash',
    )

    with pytest.raises(InvalidBinaryVersion) as exc:
        query_engine.ensure_binary()
        # "{self.name} binary version {version} is not {ENGINE_VERSION}"
    assert exc.match(
        f'{query_engine.name} binary version unexpected-hash is not {ENGINE_VERSION}'
    )


# TODO: reimplement this test
@pytest.mark.skip(
    reason='Local binary paths are no longer supported, this test still exists as support will be added again in the future'  # pylint: disable=line-too-long
)
def test_ensure_local_path(testdir: Testdir, fake_process: FakeProcess) -> None:
    """Query engine in current directory required to be the expected version"""

    fake_engine = testdir.path / ('prisma-query-engine' + PLATFORM_EXE_EXTENSION)
    fake_engine.touch()

    fake_process.register_subprocess(
        [str(fake_engine), '--version'],
        stdout='query-engine a-different-hash',
    )
    # with pytest.raises(errors.MismatchedVersionsError):
    #     TODO: handle this case
    #     pass

    fake_process.register_subprocess(
        [fake_engine, '--version'],  # type: ignore[list-item]
        stdout=f'query-engine {ENGINE_VERSION}',
    )
    # path = utils.ensure()
    # assert path == fake_engine


def test_ensure_env_override(testdir: Testdir, fake_process: FakeProcess) -> None:
    """Query engine path in environment variable can be any version"""
    fake_engine = testdir.path / 'my-query-engine'
    fake_engine.touch()
    fake_process.register_subprocess(
        [str(fake_engine), '--version'],
        stdout='query-engine a-different-hash',
    )

    with temp_env_update({'PRISMA_QUERY_ENGINE_BINARY': str(fake_engine)}):
        prisma_settings = PrismaSettings()
        engines = engines_from_settings(prisma_settings)
        query_engine = engines[0]  # query engine is the first engine
        with pytest.raises(InvalidBinaryVersion) as exc:
            query_engine.ensure_binary()
    assert exc.match(
        f'{query_engine.name} binary version a-different-hash is not {ENGINE_VERSION}'
    )
    # query_engine.ensure_binary()


def test_ensure_env_override_does_not_exist() -> None:
    """Query engine path in environment variable not found raises an error"""

    with temp_env_update({'PRISMA_QUERY_ENGINE_BINARY': 'foo'}):
        prisma_settings = PrismaSettings()
        engines = engines_from_settings(prisma_settings)
        query_engine = engines[0]  # query engine is the first engine
        with pytest.raises(FileNotFoundError) as exc:
            query_engine.ensure_binary()

    # f"{self.name} binary not found at {self.path}\nTry running `prisma fetch`"
    assert exc.match(
        f'{query_engine.name} binary not found at {query_engine.path}\nTry running `prisma fetch`'
    )
