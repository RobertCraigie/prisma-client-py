import shutil
from typing import Any

import requests

from ._types import Method
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response', 'client')


class HTTP(AbstractHTTP[requests.Session, requests.Response]):
    # pylint: disable=attribute-defined-outside-init
    session: requests.Session

    def download(self, url: str, dest: str) -> None:
        with self.session.request('GET', url, stream=True) as resp:
            with open(dest, 'wb') as fd:
                shutil.copyfileobj(resp.raw, fd)

    def request(self, method: Method, url: str, **kwargs: Any) -> 'Response':
        return Response(self.session.request(method, url, **kwargs))

    def open(self) -> None:
        self.session = requests.Session()

    def close(self) -> None:
        if not self.closed:
            self.session.close()
            self.session = None  # type: ignore[assignment]

    def __del__(self) -> None:
        self.close()

    @property
    def library(self) -> str:
        return 'requests'


client = HTTP()


class Response(AbstractResponse[requests.Response]):
    @property
    def status(self) -> int:
        return self.original.status_code

    def json(self) -> Any:
        return self.original.json()

    def text(self) -> Any:
        return self.original.text
