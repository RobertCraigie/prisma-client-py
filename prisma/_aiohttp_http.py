from typing import Any, Optional

import aiohttp

from ._types import Method
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response')


class HTTP(AbstractHTTP):
    # pylint: disable=invalid-overridden-method

    library = 'aiohttp'

    def __init__(self) -> None:
        self.session = None  # type: Optional[aiohttp.ClientSession]
        self.open()

    @staticmethod
    async def download(url: str, dest: str) -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(url, timeout=None) as resp:
                with open(dest, 'wb') as fd:
                    # TODO: read and write in chunks
                    fd.write(await resp.read())

    async def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        if self.session is None:
            self.session = aiohttp.ClientSession()

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

    def __str__(self) -> str:
        return f'<Response wrapped={self._original} >'
