from typing import Any

import httpx

from ._types import Method
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response', 'client')


class HTTP(AbstractHTTP[httpx.AsyncClient, httpx.Response]):
    # pylint: disable=invalid-overridden-method,attribute-defined-outside-init

    session: httpx.AsyncClient

    async def download(self, url: str, dest: str) -> None:
        # pyright thinks that stream() doesn't return a context manager
        # due to how httpx handles compatability imports
        # https://github.com/encode/httpx/discussions/1829
        async with self.session.stream(
            'GET', url, timeout=None
        ) as resp:  # pyright: reportGeneralTypeIssues=false
            with open(dest, 'wb') as fd:
                async for chunk in resp.aiter_bytes():
                    fd.write(chunk)

    async def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        return Response(await self.session.request(method, url, **kwargs))

    def open(self) -> None:
        self.session = httpx.AsyncClient()

    async def close(self) -> None:
        if not self.closed:
            await self.session.aclose()

            # mypy doesn't like us assigning None as the type of
            # session is not optional, however the argument that
            # the setter takes is optional, so this is fine
            self.session = None  # type: ignore[assignment]


client: HTTP = HTTP()


class Response(AbstractResponse[httpx.Response]):
    # pylint: disable=invalid-overridden-method

    @property
    def status(self) -> int:
        return self.original.status_code

    async def json(self, **kwargs: Any) -> Any:
        return self.original.json(**kwargs)

    async def text(self, **kwargs: Any) -> Any:
        return self.original.content.decode(**kwargs)
