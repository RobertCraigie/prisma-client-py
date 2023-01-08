from typing import Iterator

import pytest

from prisma import Prisma
from prisma.middleware import (
    MiddlewareParams,
    NextMiddleware,
    MiddlewareResult,
)

# TODO: more tests
# TODO: test every action


@pytest.fixture(autouse=True)
def cleanup_middlewares(client: Prisma) -> Iterator[None]:
    middlewares = client._middlewares.copy()

    client._middlewares.clear()

    try:
        yield
    finally:
        client._middlewares = middlewares


@pytest.mark.asyncio
async def test_basic(client: Prisma) -> None:
    __ran__ = False

    async def middleware(
        params: MiddlewareParams, get_result: NextMiddleware
    ) -> MiddlewareResult:
        nonlocal __ran__

        __ran__ = True
        return await get_result(params)

    client.use(middleware)
    await client.user.create({'name': 'Robert'})
    assert __ran__ is True
