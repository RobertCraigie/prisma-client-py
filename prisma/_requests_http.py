import shutil
from typing import Optional, Any

import requests

from ._types import Method
from .errors import HTTPClientClosedError
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response', 'client')


class HTTP(AbstractHTTP[requests.Session, requests.Response]):
    # pylint: disable=attribute-defined-outside-init

    library = 'requests'

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

    def close(self, session: Optional[requests.Session] = None) -> None:
        session = session or self.session
        if session is not None:
            session.close()
            self.session = None

    def __del__(self) -> None:
        self.close()


client = HTTP()


class Response(AbstractResponse[requests.Response]):
    @property
    def status(self) -> int:
        return self.original.status_code

    def json(self) -> Any:
        return self.original.json()

    def text(self) -> Any:
        return self.original.text
