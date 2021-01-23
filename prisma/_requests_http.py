import shutil
from typing import Optional, Any

import requests

from ._types import Method
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response')


class HTTP(AbstractHTTP):

    library = 'requests'

    def __init__(self) -> None:
        self.session = None  # type: Optional[requests.Session]
        self.open()

    @staticmethod
    def download(url: str, dest: str) -> None:
        with requests.get(url, stream=True) as resp:
            with open(dest, 'wb') as fd:
                shutil.copyfileobj(resp.raw, fd)

    def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        if self.session is None:
            self.session = requests.Session()

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

    def __str__(self) -> str:
        return f'<Response wrapped={self._original} >'
