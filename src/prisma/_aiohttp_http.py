import asyncio
from typing import Any

import aiohttp

from ._types import Method
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response', 'client')


class HTTP(AbstractHTTP[aiohttp.ClientSession, aiohttp.ClientResponse]):
    # pylint: disable=invalid-overridden-method,attribute-defined-outside-init

    session: aiohttp.ClientSession

    async def download(self, url: str, dest: str) -> None:
        async with self.session.get(url, raise_for_status=True, timeout=None) as resp:
            with open(dest, 'wb') as fd:
                # TODO: read and write in chunks
                fd.write(await resp.read())

    async def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        return Response(await self.session.request(method, url, **kwargs))

    def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if not self.closed:
            await self.session.close()

            # mypy doesn't like us assigning None as the type of
            # session is not optional, however the argument that
            # the setter takes is optional, so this is fine
            self.session = None  # type: ignore[assignment]

    def __del__(self) -> None:
        try:
            # avoid creating the coroutine until we know we can
            # create a task to run it to avoid coroutine
            # not awaited errors
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                return

            create_task = loop.create_task
            create_task(self.close())
        except Exception:  # pylint: disable=broad-except
            # weird errors can happen, like the asyncio module not
            # being populated, can safely ignore as we're just
            # cleaning up anyway
            pass

    @property
    def library(self) -> str:
        return 'aiohttp'


client: HTTP = HTTP()


class Response(AbstractResponse[aiohttp.ClientResponse]):
    # pylint: disable=invalid-overridden-method

    @property
    def status(self) -> int:
        return self.original.status

    async def json(self, **kwargs: Any) -> Any:
        return await self.original.json(**kwargs)

    async def text(self, **kwargs: Any) -> Any:
        return await self.original.text(**kwargs)
