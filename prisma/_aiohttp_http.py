import asyncio
from typing import Any, Optional

import aiohttp

from ._types import Method
from .errors import HTTPClientClosedError
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response', 'client')


class HTTP(AbstractHTTP):
    # pylint: disable=invalid-overridden-method

    library = 'aiohttp'

    def __init__(self) -> None:
        self.session = None  # type: Optional[aiohttp.ClientSession]
        self.open()

    def __del__(self) -> None:
        try:
            asyncio.get_event_loop().create_task(self.close())
        except Exception:  # pylint: disable=broad-except
            # weird errors can happen, like the asyncio module not
            # being populated, can safely ignore as we're just
            # cleaning up anyway
            pass

    async def download(self, url: str, dest: str) -> None:
        if self.session is None:
            raise HTTPClientClosedError()

        async with self.session.get(url, raise_for_status=True, timeout=None) as resp:
            with open(dest, 'wb') as fd:
                # TODO: read and write in chunks
                fd.write(await resp.read())

    async def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        if self.closed:
            raise HTTPClientClosedError()

        assert self.session is not None
        return Response(await self.session.request(method, url, **kwargs))

    def open(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
            self.session = None

    @property
    def closed(self) -> bool:
        return self.session is None


client = HTTP()


class Response(AbstractResponse):
    # pylint: disable=invalid-overridden-method

    def __init__(self, original: aiohttp.ClientResponse) -> None:
        self._original = original

    @property
    def status(self) -> int:
        return self._original.status

    async def json(self, **kwargs: Any) -> Any:
        return await self._original.json(**kwargs)

    async def text(self, **kwargs: Any) -> Any:
        return await self._original.text(**kwargs)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'<Response wrapped={self._original} >'
