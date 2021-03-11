import shutil
from typing import Optional, Any

import requests

from ._types import Method
from .errors import HTTPClientClosedError
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response', 'client')


class HTTP(AbstractHTTP):

    library = 'requests'

    def __init__(self) -> None:
        self.session = None  # type: Optional[requests.Session]
        self.open()

    def __del__(self) -> None:
        self.close()

    def download(self, url: str, dest: str) -> None:
        if self.session is None:
            raise HTTPClientClosedError()

        with self.session.request('GET', url, stream=True) as resp:
            with open(dest, 'wb') as fd:
                shutil.copyfileobj(resp.raw, fd)

    def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        if self.closed:
            raise HTTPClientClosedError()

        assert self.session is not None
        return Response(self.session.request(method, url, **kwargs))

    def open(self) -> None:
        self.session = requests.Session()

    def close(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None

    @property
    def closed(self) -> bool:
        return self.session is None


client = HTTP()


class Response(AbstractResponse):
    def __init__(self, original: requests.Response) -> None:
        self._original = original

    @property
    def status(self) -> int:
        return self._original.status_code

    def json(self) -> Any:
        return self._original.json()

    def text(self) -> Any:
        return self._original.text

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'<Response wrapped={self._original} >'
