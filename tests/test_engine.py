import signal
import asyncio
import contextlib
from typing import Iterator, Optional
from pathlib import Path

import pytest
from pytest_subprocess import FakeProcess
from _pytest.monkeypatch import MonkeyPatch

from prisma import BINARY_PATHS, Prisma, config
from prisma.utils import temp_env_update
from prisma.engine import utils, errors
from prisma._compat import get_running_loop
from prisma.binaries import platform
from prisma.engine.query import QueryEngine

from .utils import Testdir, skipif_windows


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


@pytest.mark.asyncio
@skipif_windows
async def test_engine_process_sigint_mask() -> None:
    """Block SIGINT in current process"""
    signal.pthread_sigmask(signal.SIG_BLOCK, [signal.SIGINT])
    db = Prisma()
    await db.connect()

    with pytest.raises(errors.AlreadyConnectedError):
        await db.connect()

    await asyncio.wait_for(db.disconnect(), timeout=5)
    signal.pthread_sigmask(signal.SIG_UNBLOCK, [signal.SIGINT])


@pytest.mark.asyncio
@skipif_windows
async def test_engine_process_sigterm_mask() -> None:
    """Block SIGTERM in current process"""
    signal.pthread_sigmask(signal.SIG_BLOCK, [signal.SIGTERM])
    db = Prisma()
    await db.connect()

    with pytest.raises(errors.AlreadyConnectedError):
        await db.connect()

    await asyncio.wait_for(db.disconnect(), timeout=5)
    signal.pthread_sigmask(signal.SIG_UNBLOCK, [signal.SIGTERM])


def test_stopping_engine_on_closed_loop() -> None:
    """Stopping the engine with no event loop available does not raise an error"""
    with no_event_loop():
        engine = QueryEngine(dml_path=Path.cwd())
        engine.stop()


def test_engine_binary_does_not_exist(monkeypatch: MonkeyPatch) -> None:
    """No query engine binary found raises an error"""

    def mock_exists(path: Path) -> bool:
        return False

    monkeypatch.setattr(Path, 'exists', mock_exists, raising=True)

    with pytest.raises(errors.BinaryNotFoundError) as exc:
        utils.ensure(BINARY_PATHS.query_engine)

    assert exc.match(
        r'Expected .*, .* or .* to exist but none were found or could not be executed\.\nTry running prisma py fetch'
    )


def test_engine_binary_does_not_exist_no_binary_paths(
    monkeypatch: MonkeyPatch,
) -> None:
    """No query engine binary found raises an error"""

    def mock_exists(path: Path) -> bool:
        return False

    monkeypatch.setattr(Path, 'exists', mock_exists, raising=True)

    with pytest.raises(errors.BinaryNotFoundError) as exc:
        utils.ensure({})

    assert exc.match(
        r'Expected .* or .* to exist but neither were found or could not be executed\.\nTry running prisma py fetch'
    )


def test_mismatched_version_error(fake_process: FakeProcess) -> None:
    """Mismatched query engine versions raises an error"""

    fake_process.register_subprocess(
        [
            str(utils._resolve_from_binary_paths(BINARY_PATHS.query_engine)),
            '--version',
        ],
        stdout='query-engine unexpected-hash',
    )

    with pytest.raises(errors.MismatchedVersionsError) as exc:
        utils.ensure(BINARY_PATHS.query_engine)

    assert exc.match(f'Expected query engine version `{config.expected_engine_version}` but got `unexpected-hash`')


def test_ensure_local_path(testdir: Testdir, fake_process: FakeProcess) -> None:
    """Query engine in current directory required to be the expected version"""

    fake_engine = testdir.path / platform.check_for_extension(f'prisma-query-engine-{platform.binary_platform()}')
    fake_engine.touch()

    fake_process.register_subprocess(
        [str(fake_engine), '--version'],
        stdout='query-engine a-different-hash',
    )
    with pytest.raises(errors.MismatchedVersionsError):
        path = utils.ensure(BINARY_PATHS.query_engine)

    fake_process.register_subprocess(
        [str(fake_engine), '--version'],
        stdout=f'query-engine {config.expected_engine_version}',
    )
    path = utils.ensure(BINARY_PATHS.query_engine)
    assert path == fake_engine


def test_ensure_env_override(testdir: Testdir, fake_process: FakeProcess) -> None:
    """Query engine path in environment variable can be any version"""
    fake_engine = testdir.path / 'my-query-engine'
    fake_engine.touch()

    fake_process.register_subprocess(
        [str(fake_engine), '--version'],
        stdout='query-engine a-different-hash',
    )

    with temp_env_update({'PRISMA_QUERY_ENGINE_BINARY': str(fake_engine)}):
        path = utils.ensure(BINARY_PATHS.query_engine)

    assert path == fake_engine


def test_ensure_env_override_does_not_exist() -> None:
    """Query engine path in environment variable not found raises an error"""
    with temp_env_update({'PRISMA_QUERY_ENGINE_BINARY': 'foo'}):
        with pytest.raises(errors.BinaryNotFoundError) as exc:
            utils.ensure(BINARY_PATHS.query_engine)

    assert exc.match(r'PRISMA_QUERY_ENGINE_BINARY was provided, but no query engine was found at foo')
