from __future__ import annotations

import os
import sys
import json
import time
import atexit
import signal
import asyncio
import logging
import subprocess
from typing import TYPE_CHECKING, Any, overload
from pathlib import Path
from datetime import timedelta
from typing_extensions import Literal, override

from . import utils, errors
from ._http import SyncHTTPEngine, AsyncHTTPEngine
from ..utils import DEBUG, _env_bool, time_since
from .._types import HttpConfig, TransactionId
from .._builder import dumps
from ..binaries import platform
from .._constants import DEFAULT_CONNECT_TIMEOUT

if TYPE_CHECKING:
    from ..types import MetricsFormat, DatasourceOverride  # noqa: TID251


__all__ = (
    'SyncQueryEngine',
    'AsyncQueryEngine',
)

log: logging.Logger = logging.getLogger(__name__)


class BaseQueryEngine:
    dml_path: Path
    url: str | None
    file: Path | None
    process: subprocess.Popen[bytes] | subprocess.Popen[str] | None

    def __init__(
        self,
        *,
        dml_path: Path,
        log_queries: bool = False,
    ) -> None:
        self.dml_path = dml_path
        self._log_queries = log_queries
        self.process = None
        self.file = None

    def _ensure_file(self) -> Path:
        # circular import
        from ..client import BINARY_PATHS  # noqa: TID251

        return utils.ensure(BINARY_PATHS.query_engine)

    def _spawn_process(
        self,
        *,
        file: Path,
        datasources: list[DatasourceOverride] | None,
    ) -> tuple[str, subprocess.Popen[bytes] | subprocess.Popen[str]]:
        port = utils.get_open_port()
        log.debug('Running query engine on port %i', port)

        self.url = f'http://localhost:{port}'

        env = os.environ.copy()
        env.update(
            PRISMA_DML_PATH=str(self.dml_path.absolute()),
            RUST_LOG='error',
            RUST_LOG_FORMAT='json',
            PRISMA_CLIENT_ENGINE_TYPE='binary',
            PRISMA_ENGINE_PROTOCOL='graphql',
        )

        if DEBUG:
            env.update(RUST_LOG='info')

        if datasources is not None:
            env.update(OVERWRITE_DATASOURCES=dumps(datasources))

        # TODO: remove the noise from these query logs
        if self._log_queries:
            env.update(LOG_QUERIES='y')

        args: list[str] = [
            str(file.absolute()),
            '-p',
            str(port),
            '--enable-metrics',
            '--enable-raw-queries',
        ]
        if _env_bool('__PRISMA_PY_PLAYGROUND'):
            env.update(RUST_LOG='info')
            args.append('--enable-playground')

        log.debug('Starting query engine...')
        popen_kwargs: dict[str, Any] = {
            'env': env,
            'stdout': sys.stdout,
            'stderr': sys.stderr,
            'text': False,
        }
        if platform.name() != 'windows':
            # ensure SIGINT is unblocked before forking the query engine
            # https://github.com/RobertCraigie/prisma-client-py/pull/678
            popen_kwargs['preexec_fn'] = lambda: signal.pthread_sigmask(
                signal.SIG_UNBLOCK, [signal.SIGINT, signal.SIGTERM]
            )

        self.process = subprocess.Popen(args, **popen_kwargs)

        return self.url, self.process

    def _kill_process(self, timeout: timedelta | None) -> None:
        if self.process is None:
            return

        if timeout is not None:
            total_seconds = timeout.total_seconds()
        else:
            total_seconds = None

        if platform.name() == 'windows':
            self.process.kill()
            self.process.wait(timeout=total_seconds)
        else:
            self.process.send_signal(signal.SIGINT)
            try:
                self.process.wait(timeout=total_seconds)
            except subprocess.TimeoutExpired:
                self.process.send_signal(signal.SIGKILL)

        self.process = None


class SyncQueryEngine(BaseQueryEngine, SyncHTTPEngine):
    file: Path | None

    def __init__(
        self,
        *,
        dml_path: Path,
        log_queries: bool = False,
        http_config: HttpConfig | None = None,
    ) -> None:
        # this is a little weird but it's needed to distinguish between
        # the different required arguments for our two base classes
        BaseQueryEngine.__init__(self, dml_path=dml_path, log_queries=log_queries)
        SyncHTTPEngine.__init__(self, url=None, **(http_config or {}))

        # ensure the query engine process is terminated when we are
        atexit.register(self.stop)

    @override
    def close(self, *, timeout: timedelta | None = None) -> None:
        log.debug('Disconnecting query engine...')

        self._kill_process(timeout=timeout)
        self._close_session()

        log.debug('Disconnected query engine')

    @override
    async def aclose(self, *, timeout: timedelta | None = None) -> None:
        self.close(timeout=timeout)
        self._close_session()

    @override
    def connect(
        self,
        timeout: timedelta = DEFAULT_CONNECT_TIMEOUT,
        datasources: list[DatasourceOverride] | None = None,
    ) -> None:
        log.debug('Connecting to query engine')
        if datasources:
            log.debug('Datasources: %s', datasources)

        if self.process is not None:
            raise errors.AlreadyConnectedError('Already connected to the query engine')

        start = time.monotonic()
        self.file = file = self._ensure_file()

        try:
            self.spawn(file, timeout=timeout, datasources=datasources)
        except Exception:
            self.close()
            raise

        log.debug('Connecting to query engine took %s', time_since(start))

    def spawn(
        self,
        file: Path,
        timeout: timedelta = DEFAULT_CONNECT_TIMEOUT,
        datasources: list[DatasourceOverride] | None = None,
    ) -> None:
        self._spawn_process(file=file, datasources=datasources)

        last_exc = None
        for _ in range(int(timeout.total_seconds() / 0.1)):
            try:
                data = self.request('GET', '/status')
            except Exception as exc:
                # TODO(someday): only retry on ConnectionError
                if isinstance(exc, AttributeError):
                    raise

                last_exc = exc
                log.debug(
                    'Could not connect to query engine due to %s; retrying...',
                    exc,
                )
                time.sleep(0.1)
                continue

            if data.get('Errors') is not None:
                log.debug('Could not connect due to gql errors; retrying...')
                time.sleep(0.1)
                continue

            break
        else:
            raise errors.EngineConnectionError('Could not connect to the query engine') from last_exc

    @override
    def query(
        self,
        content: str,
        *,
        tx_id: TransactionId | None,
    ) -> Any:
        headers: dict[str, str] = {}
        if tx_id is not None:
            headers['X-transaction-id'] = tx_id

        return self.request(
            'POST',
            '/',
            content=content,
            headers=headers,
        )

    @override
    def start_transaction(self, *, content: str) -> TransactionId:
        result = self.request(
            'POST',
            '/transaction/start',
            content=content,
        )
        return TransactionId(result['id'])

    @override
    def commit_transaction(self, tx_id: TransactionId) -> None:
        self.request('POST', f'/transaction/{tx_id}/commit')

    @override
    def rollback_transaction(self, tx_id: TransactionId) -> None:
        self.request('POST', f'/transaction/{tx_id}/rollback')

    @overload
    def metrics(
        self,
        *,
        format: Literal['json'],
        global_labels: dict[str, str] | None,
    ) -> dict[str, Any]: ...

    @overload
    def metrics(
        self,
        *,
        format: Literal['prometheus'],
        global_labels: dict[str, str] | None,
    ) -> str: ...

    @override
    def metrics(
        self,
        *,
        format: MetricsFormat,
        global_labels: dict[str, str] | None,
    ) -> str | dict[str, Any]:
        if global_labels is not None:
            content = json.dumps(global_labels)
        else:
            content = None

        return self.request(  # type: ignore[no-any-return]
            'GET',
            f'/metrics?format={format}',
            content=content,
            parse_response=format == 'json',
        )


class AsyncQueryEngine(BaseQueryEngine, AsyncHTTPEngine):
    file: Path | None

    def __init__(
        self,
        *,
        dml_path: Path,
        log_queries: bool = False,
        http_config: HttpConfig | None = None,
    ) -> None:
        # this is a little weird but it's needed to distinguish between
        # the different required arguments for our two base classes
        BaseQueryEngine.__init__(self, dml_path=dml_path, log_queries=log_queries)
        AsyncHTTPEngine.__init__(self, url=None, **(http_config or {}))

        # ensure the query engine process is terminated when we are
        atexit.register(self.stop)

    @override
    def close(self, *, timeout: timedelta | None = None) -> None:
        log.debug('Disconnecting query engine...')

        self._kill_process(timeout=timeout)

        log.debug('Disconnected query engine')

    @override
    async def aclose(self, *, timeout: timedelta | None = None) -> None:
        self.close(timeout=timeout)
        await self._close_session()

    @override
    async def connect(
        self,
        timeout: timedelta = DEFAULT_CONNECT_TIMEOUT,
        datasources: list[DatasourceOverride] | None = None,
    ) -> None:
        log.debug('Connecting to query engine')
        if datasources:
            log.debug('Datasources: %s', datasources)

        if self.process is not None:
            raise errors.AlreadyConnectedError('Already connected to the query engine')

        start = time.monotonic()
        self.file = file = self._ensure_file()

        try:
            await self.spawn(file, timeout=timeout, datasources=datasources)
        except Exception:
            self.close()
            raise

        log.debug('Connecting to query engine took %s', time_since(start))

    async def spawn(
        self,
        file: Path,
        timeout: timedelta = DEFAULT_CONNECT_TIMEOUT,
        datasources: list[DatasourceOverride] | None = None,
    ) -> None:
        self._spawn_process(file=file, datasources=datasources)

        last_exc = None
        for _ in range(int(timeout.total_seconds() / 0.1)):
            try:
                data = await self.request('GET', '/status')
            except Exception as exc:
                # TODO(someday): only retry on ConnectionError
                if isinstance(exc, AttributeError):
                    raise

                last_exc = exc
                log.debug(
                    'Could not connect to query engine due to %s; retrying...',
                    exc,
                )
                await asyncio.sleep(0.1)
                continue

            if data.get('Errors') is not None:
                log.debug('Could not connect due to gql errors; retrying...')
                await asyncio.sleep(0.1)
                continue

            break
        else:
            raise errors.EngineConnectionError('Could not connect to the query engine') from last_exc

    @override
    async def query(
        self,
        content: str,
        *,
        tx_id: TransactionId | None,
    ) -> Any:
        headers: dict[str, str] = {}
        if tx_id is not None:
            headers['X-transaction-id'] = tx_id

        return await self.request(
            'POST',
            '/',
            content=content,
            headers=headers,
        )

    @override
    async def start_transaction(self, *, content: str) -> TransactionId:
        result = await self.request(
            'POST',
            '/transaction/start',
            content=content,
        )
        return TransactionId(result['id'])

    @override
    async def commit_transaction(self, tx_id: TransactionId) -> None:
        await self.request('POST', f'/transaction/{tx_id}/commit')

    @override
    async def rollback_transaction(self, tx_id: TransactionId) -> None:
        await self.request('POST', f'/transaction/{tx_id}/rollback')

    @overload
    async def metrics(
        self,
        *,
        format: Literal['json'],
        global_labels: dict[str, str] | None,
    ) -> dict[str, Any]: ...

    @overload
    async def metrics(
        self,
        *,
        format: Literal['prometheus'],
        global_labels: dict[str, str] | None,
    ) -> str: ...

    @override
    async def metrics(
        self,
        *,
        format: MetricsFormat,
        global_labels: dict[str, str] | None,
    ) -> str | dict[str, Any]:
        if global_labels is not None:
            content = json.dumps(global_labels)
        else:
            content = None

        return await self.request(  # type: ignore[no-any-return]
            'GET',
            f'/metrics?format={format}',
            content=content,
            parse_response=format == 'json',
        )
