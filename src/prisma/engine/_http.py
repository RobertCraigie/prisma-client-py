from __future__ import annotations

import json
import logging
from typing import Any, NoReturn
from datetime import timedelta
from typing_extensions import override

import httpx

from . import utils, errors
from ..utils import is_dict
from .._types import Method
from ._abstract import SyncAbstractEngine, AsyncAbstractEngine
from .._sync_http import SyncHTTP
from .._async_http import AsyncHTTP
from ..http_abstract import AbstractResponse

log: logging.Logger = logging.getLogger(__name__)


class BaseHTTPEngine:
    """Engine wrapper that communicates to the underlying engine over HTTP"""

    url: str | None
    headers: dict[str, str]

    def __init__(
        self,
        *,
        url: str | None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.url = url
        self.headers = headers if headers is not None else {}

    def _build_request(
        self,
        *,
        path: str,
        method: Method,
        content: Any,
        headers: dict[str, str] | None,
        parse_response: bool,
    ) -> tuple[str, dict[str, Any]]:
        if self.url is None:
            raise errors.NotConnectedError('Not connected to the query engine')

        kwargs = {
            'headers': {
                **self.headers,
            }
        }

        if parse_response:
            kwargs['headers']['Accept'] = 'application/json'

        if headers is not None:
            kwargs['headers'].update(headers)

        if content is not None:
            kwargs['content'] = content

        url = self.url + path
        log.debug('Constructed %s request to %s', method, url)
        log.debug('Request headers: %s', kwargs['headers'])
        log.debug('Request content: %s', content)

        return url, kwargs

    def _process_response_data(
        self,
        *,
        data: object,
        response: AbstractResponse[httpx.Response],
    ) -> Any:
        if isinstance(data, str):
            # workaround for https://github.com/prisma/prisma-engines/pull/4246
            data = json.loads(data)

        if not is_dict(data):
            raise TypeError(f'Expected deserialised engine response to be a dictionary, got {type(data)} - {data}')

        errors_data = data.get('errors')
        if errors_data:
            return utils.handle_response_errors(response, errors_data)

        return data

    def _process_response_error(
        self,
        *,
        body: str,
        response: AbstractResponse[httpx.Response],
    ) -> NoReturn:
        if response.status == 422:
            raise errors.UnprocessableEntityError(response)

        # TODO: handle errors better
        raise errors.EngineRequestError(response, body)


class SyncHTTPEngine(BaseHTTPEngine, SyncAbstractEngine):
    session: SyncHTTP

    def __init__(
        self,
        url: str | None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(url=url, headers=headers)
        self.session = SyncHTTP(**kwargs)

    @override
    def close(
        self,
        *,
        timeout: timedelta | None = None,  # noqa: ARG002
    ) -> None:
        self._close_session()

    @override
    async def aclose(self, *, timeout: timedelta | None = None) -> None:
        pass

    def _close_session(self) -> None:
        if self.session and not self.session.closed:
            self.session.close()

    # TODO: improve return types
    def request(
        self,
        method: Method,
        path: str,
        *,
        content: Any = None,
        headers: dict[str, str] | None = None,
        parse_response: bool = True,
    ) -> Any:
        url, kwargs = self._build_request(
            path=path,
            method=method,
            content=content,
            headers=headers,
            parse_response=parse_response,
        )

        response = self.session.request(method, url, **kwargs)
        log.debug('%s %s returned status %s', method, url, response.status)

        if 300 > response.status >= 200:
            # In certain cases we just want to return the response content as-is.
            #
            # This is useful for metrics which can be returned in a Prometheus format
            # which is incompatible with JSON.
            if not parse_response:
                text = response.text()
                log.debug('%s %s returned text: %s', method, url, text)
                return text

            data = response.json()
            log.debug('%s %s returned %s', method, url, data)

            return self._process_response_data(data=data, response=response)

        self._process_response_error(body=response.text(), response=response)


class AsyncHTTPEngine(BaseHTTPEngine, AsyncAbstractEngine):
    session: AsyncHTTP

    def __init__(
        self,
        url: str | None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(url=url, headers=headers)
        self.session = AsyncHTTP(**kwargs)

    @override
    def close(self, *, timeout: timedelta | None = None) -> None:
        pass

    @override
    async def aclose(
        self,
        *,
        timeout: timedelta | None = None,  # noqa: ARG002
    ) -> None:
        await self._close_session()

    async def _close_session(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    # TODO: improve return types
    async def request(
        self,
        method: Method,
        path: str,
        *,
        content: Any = None,
        headers: dict[str, str] | None = None,
        parse_response: bool = True,
    ) -> Any:
        url, kwargs = self._build_request(
            path=path,
            method=method,
            content=content,
            headers=headers,
            parse_response=parse_response,
        )

        response = await self.session.request(method, url, **kwargs)
        log.debug('%s %s returned status %s', method, url, response.status)

        if 300 > response.status >= 200:
            # In certain cases we just want to return the response content as-is.
            #
            # This is useful for metrics which can be returned in a Prometheus format
            # which is incompatible with JSON.
            if not parse_response:
                text = await response.text()
                log.debug('%s %s returned text: %s', method, url, text)
                return text

            data = await response.json()
            log.debug('%s %s returned %s', method, url, data)

            return self._process_response_data(data=data, response=response)

        self._process_response_error(body=await response.text(), response=response)
