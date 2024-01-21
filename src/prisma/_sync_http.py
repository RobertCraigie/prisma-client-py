from typing import Any
from typing_extensions import override

import httpx

from ._types import Method
from .http_abstract import AbstractHTTP, AbstractResponse

__all__ = ('HTTP', 'SyncHTTP', 'Response', 'client')


class SyncHTTP(AbstractHTTP[httpx.Client, httpx.Response]):
    session: httpx.Client

    @override
    def download(self, url: str, dest: str) -> None:
        with self.session.stream('GET', url, timeout=None) as resp:
            resp.raise_for_status()
            with open(dest, 'wb') as fd:
                for chunk in resp.iter_bytes():
                    fd.write(chunk)

    @override
    def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        return Response(self.session.request(method, url, **kwargs))

    @override
    def open(self) -> None:
        self.session = httpx.Client(**self.session_kwargs)

    @override
    def close(self) -> None:
        if self.should_close():
            self.session.close()
            self.session = None  # type: ignore[assignment]

    def __del__(self) -> None:
        self.close()


HTTP = SyncHTTP

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
    def json(self, **kwargs: Any) -> Any:
        return self.original.json(**kwargs)

    @override
    def text(self, **kwargs: Any) -> str:
        return self.original.content.decode(**kwargs)
