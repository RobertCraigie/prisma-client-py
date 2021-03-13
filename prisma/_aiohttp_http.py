import asyncio
from typing import Any, Optional, Dict

import aiohttp

from ._types import Method
from .errors import HTTPClientClosedError
from .http_abstract import AbstractResponse, AbstractHTTP


__all__ = ('HTTP', 'Response', 'client')


class HTTP(AbstractHTTP[aiohttp.ClientSession, aiohttp.ClientResponse]):
    # pylint: disable=invalid-overridden-method,attribute-defined-outside-init

    library = 'aiohttp'

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

    async def close(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        session = session or self.session
        self.session = None
        if session is not None:
            await session.close()

    def __del__(self) -> None:
        # NOTE: this should be removed in the next commit
        # where I introduce lazy session loading
        # note to self, also remove the pylintrc change
        def handler(self: asyncio.AbstractEventLoop, context: Dict[str, Any]) -> None:
            # if aiohttp calls the exception handler, ignore it as it is just warning
            # that the client session is not closed
            if context and 'client_session' not in context:
                if old_handler:
                    old_handler(self, context)
                else:
                    loop.default_exception_handler(context)

        session = self.session
        self.session = None
        loop = asyncio.get_event_loop()
        loop.create_task(self.close(session))

        old_handler = loop.get_exception_handler()
        loop.set_exception_handler(handler)


client = HTTP()


class Response(AbstractResponse[aiohttp.ClientResponse]):
    # pylint: disable=invalid-overridden-method

    @property
    def status(self) -> int:
        return self.original.status

    async def json(self, **kwargs: Any) -> Any:
        return await self.original.json(**kwargs)

    async def text(self, **kwargs: Any) -> Any:
        return await self.original.text(**kwargs)
