import os
import sys
import time
import signal
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional

import aiohttp
from pydantic import BaseModel

from . import utils, errors
from ..utils import time_since
from ..binaries import platform


__all__ = ('QueryEngine',)

log = logging.getLogger(__name__)


class QueryEngine(BaseModel):
    url: Optional[str]
    session: Optional[aiohttp.ClientSession]
    process: Optional[subprocess.Popen]
    file: Optional[Path]
    dml: str

    class Config:
        arbitrary_types_allowed = True

    def __del__(self):
        self.stop()

    def stop(self):
        self.disconnect()
        asyncio.get_event_loop().create_task(self.close_session())

    def disconnect(self):
        log.debug('Disconnecting query engine...')

        if self.process is not None:
            if platform.name() == 'windows':
                self.process.kill()
            else:
                self.process.send_signal(signal.SIGINT)

            self.process.wait()
            self.process = None

        log.debug('Disconnected query engine')

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def connect(self):
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

    async def spawn(self, file):
        port = utils.get_open_port()
        log.debug('Running query engine on port %i', port)

        self.url = f'http://localhost:{port}'

        env = dict(
            **os.environ,
            PRISMA_DML=self.dml,
            RUST_LOG='error',
            RUST_LOG_FORMAT='json',
        )
        if log.isEnabledFor(logging.DEBUG):
            env.update(PRISMA_LOG_QUERIES='y', RUST_LOG='info')

        log.debug('Starting query engine...')
        self.process = subprocess.Popen(
            [file.absolute(), '-p', str(port), '--enable-raw-queries'],
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        # send a health check and retry if not successful
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

    async def request(self, method, path):
        if self.session is None:
            self.session = aiohttp.ClientSession()

        kwargs = {'headers': {'Content-Type': 'application/json'}}

        url = self.url + path
        async with self.session.request(method, url, **kwargs) as resp:
            if 300 > resp.status >= 200:
                return await resp.json()

            # TODO: handle errors better
            raise errors.EngineRequestError(resp, await resp.body())
