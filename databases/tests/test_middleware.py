from typing import Iterator, cast
from prisma.models import User

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


@pytest.mark.asyncio
async def test_modified_return_field(client: Prisma) -> None:
    async def middleware(
        params: MiddlewareParams, get_result: NextMiddleware
    ) -> MiddlewareResult:
        assert params.model is not None
        assert params.model.__name__ == 'User'
        assert params.method == 'create'

        result = await get_result(params)

        assert isinstance(result, User)
        result.name = 'Tegan'
        return result

    client.use(middleware)
    user = await client.user.create({'name': 'Robert'})
    assert user.name == 'Tegan'


@pytest.mark.asyncio
async def test_modified_return_type(client: Prisma) -> None:
    # TODO: note about alternatives
    class MyCustomUser(User):
        @property
        def full_name(self) -> str:
            return self.name + ' Smith'

    async def middleware(
        params: MiddlewareParams, get_result: NextMiddleware
    ) -> MiddlewareResult:
        result = await get_result(params)

        return MiddlewareResult(MyCustomUser.parse_obj(result))

    client.use(middleware)
    user = await client.user.create({'name': 'Robert'})
    assert user.name == 'Robert'
    assert isinstance(user, MyCustomUser)
    assert user.full_name == 'Robert Smith'


@pytest.mark.asyncio
async def test_modified_arguments(client: Prisma) -> None:
    async def middleware(
        params: MiddlewareParams, get_result: NextMiddleware
    ) -> MiddlewareResult:
        data = cast('dict[str, object] | None', params.arguments.get('data'))
        if data is not None:  # pragma: no branch
            name = data.get('name')
            if name == 'Robert':  # pragma: no branch
                data['name'] = 'Tegan'

        return await get_result(params)

    client.use(middleware)

    user = await client.user.create({'name': 'Robert'})
    assert user.name == 'Tegan'

    user = await client.user.create({'name': 'Alfie'})
    assert user.name == 'Alfie'
