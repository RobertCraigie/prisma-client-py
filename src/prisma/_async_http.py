import json
from typing import Any
from typing_extensions import override

import httpx

from ._types import Method
from .http_abstract import AbstractHTTP, AbstractResponse

__all__ = ('HTTP', 'AsyncHTTP', 'Response', 'client')


class AsyncHTTP(AbstractHTTP[httpx.AsyncClient, httpx.Response]):
    session: httpx.AsyncClient

    @override
    async def download(self, url: str, dest: str) -> None:
        async with self.session.stream('GET', url, timeout=None) as resp:
            resp.raise_for_status()
            with open(dest, 'wb') as fd:
                async for chunk in resp.aiter_bytes():
                    fd.write(chunk)

    @override
    async def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        return Response(await self.session.request(method, url, **kwargs))

    @override
    def open(self) -> None:
        self.session = httpx.AsyncClient(**self.session_kwargs)

    @override
    async def close(self) -> None:
        if self.should_close():
            await self.session.aclose()

            # mypy doesn't like us assigning None as the type of
            # session is not optional, however the argument that
            # the setter takes is optional, so this is fine
            self.session = None  # type: ignore[assignment]


HTTP = AsyncHTTP


client: HTTP = HTTP()


class Response(AbstractResponse[httpx.Response]):
    __slots__ = ()

    @property
    @override
    def status(self) -> int:
        return self.original.status_code

    @property
    @override
    def headers(self) -> httpx.Headers:
        return self.original.headers

    @override
    async def json(self, **kwargs: Any) -> Any:
        return json.loads(await self.original.aread(), **kwargs)

    @override
    async def text(self, **kwargs: Any) -> str:
        return ''.join([part async for part in self.original.aiter_text(**kwargs)])
