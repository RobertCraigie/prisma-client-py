import os
import sys
import time
import atexit
import signal
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional, Any

import aiohttp

from . import utils, errors
from ..utils import time_since
from ..binaries import platform


__all__ = ('QueryEngine',)

log = logging.getLogger(__name__)


class QueryEngine:
    def __init__(self, *, dml: str):
        self.dml = dml
        self.url = None  # type: Optional[str]
        self.process = None  # type: Optional[subprocess.Popen[bytes]]
        self.session = None  # type: Optional[aiohttp.ClientSession]
        self.file = None  # type: Optional[Path]

        # ensure the query engine process is terminated when we are
        atexit.register(self.stop)

    def __del__(self) -> None:
        self.stop()

    def stop(self) -> None:
        self.disconnect()
        asyncio.get_event_loop().create_task(self.close_session())

    def disconnect(self) -> None:
        log.debug('Disconnecting query engine...')

        if self.process is not None:
            if platform.name() == 'windows':
                self.process.kill()
            else:
                self.process.send_signal(signal.SIGINT)

            self.process.wait()
            self.process = None

        log.debug('Disconnected query engine')

    async def close_session(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def connect(self) -> None:
        log.debug('Connecting to query engine')
        if self.process is not None:
            raise errors.AlreadyConnectedError('Already connected to the query engine')

        start = time.monotonic()
        self.file = file = utils.ensure()

        try:
            await self.spawn(file)
        except Exception:
            self.disconnect()
            raise

        log.debug('Connecting to query engine took %s', time_since(start))

    async def spawn(self, file: Path) -> None:
        port = utils.get_open_port()
        log.debug('Running query engine on port %i', port)

        self.url = f'http://localhost:{port}'

        env = dict(
            **os.environ,
            PRISMA_DML=self.dml,
            RUST_LOG='error',
            RUST_LOG_FORMAT='json',
        )
        if os.environ.get('PRISMA_PY_DEBUG'):
            env.update(PRISMA_LOG_QUERIES='y', RUST_LOG='info')

        log.debug('Starting query engine...')
        self.process = subprocess.Popen(
            [file.absolute(), '-p', str(port), '--enable-raw-queries'],
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        last_exc = None
        for _ in range(100):
            try:
                data = await self.request('GET', '/status')
            except Exception as exc:  # pylint: disable=broad-except
                last_exc = exc
                log.debug(
                    'Could not connect to query engine due to %s; retrying...',
                    type(exc).__name__,
                )
                await asyncio.sleep(0.1)
                continue

            if data.get('Errors') is not None:
                log.debug('Could not connect due to gql errors; retrying...')
                await asyncio.sleep(0.1)
                continue

            break
        else:
            raise errors.EngineConnectionError(
                'Could not connect to the query engine'
            ) from last_exc

    async def request(self, method: str, path: str, *, data: Any = None) -> Any:
        if self.url is None:
            raise errors.NotConnectedError('Not connected to the query engine')

        kwargs = {
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        }

        if data is not None:
            kwargs['data'] = data

        url = self.url + path
        log.debug('Sending %s request to %s with data: %s', method, url, data)

        # TODO: re-use the same session
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as resp:
                if 300 > resp.status >= 200:
                    response = await resp.json()
                    log.debug('%s %s returned %s', method, url, response)

                    errors_data = response.get('errors')
                    if errors_data:
                        return utils.handle_response_errors(resp, errors_data)

                    return response

                # TODO: handle errors better
                raise errors.EngineRequestError(resp, await resp.text())
