import pytest
from prisma import Client, errors
from .utils import GRAPHQL_MAX_INT, GRAPHQL_MIN_INT


@pytest.mark.asyncio
async def test_graphql_max_int(client: Client) -> None:
    with pytest.raises(errors.DataError) as exc:
        await client.post.find_first(where={'views': {'equals': GRAPHQL_MAX_INT + 1}})

    assert exc.match('number too large to fit in target type')
    await client.post.find_first(where={'views': {'equals': GRAPHQL_MAX_INT}})

    post = await client.post.create(
        {'title': 'Foo', 'published': False, 'views': GRAPHQL_MAX_INT}
    )
    assert post.views == GRAPHQL_MAX_INT


@pytest.mark.asyncio
async def test_graphql_min_int(client: Client) -> None:
    with pytest.raises(errors.DataError) as exc:
        await client.post.find_first(where={'views': {'equals': GRAPHQL_MIN_INT - 1}})

    assert exc.match('number too small to fit in target type')
    await client.post.find_first(where={'views': {'equals': GRAPHQL_MIN_INT}})

    post = await client.post.create(
        {'title': 'Foo', 'published': False, 'views': GRAPHQL_MIN_INT}
    )
    assert post.views == GRAPHQL_MIN_INT
