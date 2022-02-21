import asyncio
import contextlib
from pathlib import Path
from typing import Iterator, Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_subprocess import FakeProcess

from prisma import Prisma
from prisma.utils import temp_env_update
from prisma.binaries import platform
from prisma.binaries import BINARIES, ENGINE_VERSION
from prisma.engine import errors, utils
from prisma.engine.query import QueryEngine
from prisma._compat import get_running_loop

from .utils import Testdir


QUERY_ENGINE = next(  # pragma: no branch
    b for b in BINARIES if b.name == 'query-engine'
)


@contextlib.contextmanager
def no_event_loop() -> Iterator[None]:
    try:
        current: Optional[asyncio.AbstractEventLoop] = get_running_loop()
    except RuntimeError:
        current = None

    # if there is no running loop then we don't touch the event loop
    # as this can cause weird issues breaking other tests
    if not current:  # pragma: no cover
        yield
    else:  # pragma: no cover
        try:
            asyncio.set_event_loop(None)
            yield
        finally:
            asyncio.set_event_loop(current)


@pytest.mark.asyncio
async def test_engine_connects() -> None:
    """Can connect to engine"""
    db = Prisma()
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

    with pytest.raises(errors.BinaryNotFoundError) as exc:
        utils.ensure()

    assert exc.match(
        r'Expected .* or .* but neither were found\.\nTry running prisma py fetch'
    )


def test_mismatched_version_error(fake_process: FakeProcess) -> None:
    """Mismatched query engine versions raises an error"""
    fake_process.register_subprocess(
        [QUERY_ENGINE.path, '--version'],  # type: ignore[list-item]
        stdout='query-engine unexpected-hash',
    )

    with pytest.raises(errors.MismatchedVersionsError) as exc:
        utils.ensure()

    assert exc.match(
        f'Expected query engine version `{ENGINE_VERSION}` but got `unexpected-hash`'
    )


def test_ensure_local_path(
    testdir: Testdir, fake_process: FakeProcess
) -> None:
    """Query engine in current directory required to be the expected version"""
    fake_engine = testdir.path / platform.check_for_extension(
        f'prisma-query-engine-{platform.binary_platform()}'
    )
    fake_engine.touch()

    fake_process.register_subprocess(
        [fake_engine, '--version'],  # type: ignore[list-item]
        stdout='query-engine a-different-hash',
    )
    with pytest.raises(errors.MismatchedVersionsError):
        path = utils.ensure()

    fake_process.register_subprocess(
        [fake_engine, '--version'],  # type: ignore[list-item]
        stdout=f'query-engine {ENGINE_VERSION}',
    )
    path = utils.ensure()
    assert path == fake_engine


def test_ensure_env_override(
    testdir: Testdir, fake_process: FakeProcess
) -> None:
    """Query engine path in environment variable can be any version"""
    fake_engine = testdir.path / 'my-query-engine'
    fake_engine.touch()

    fake_process.register_subprocess(
        [fake_engine, '--version'],  # type: ignore[list-item]
        stdout='query-engine a-different-hash',
    )

    with temp_env_update({'PRISMA_QUERY_ENGINE_BINARY': str(fake_engine)}):
        path = utils.ensure()

    assert path == fake_engine


def test_ensure_env_override_does_not_exist() -> None:
    """Query engine path in environment variable not found raises an error"""
    with temp_env_update({'PRISMA_QUERY_ENGINE_BINARY': 'foo'}):
        with pytest.raises(errors.BinaryNotFoundError) as exc:
            utils.ensure()

    assert exc.match(
        r'PRISMA_QUERY_ENGINE_BINARY was provided, but no query engine was found at foo'
    )
