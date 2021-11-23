import pytest
from prisma import Client


# TODO: more tests


@pytest.mark.asyncio
async def test_count(client: Client) -> None:
    """Basic usage with a result"""
    await client.post.create({'title': 'post 1', 'published': False})
    assert await client.post.count() == 1


@pytest.mark.asyncio
async def test_count_no_results(client: Client) -> None:
    """No results returns 0"""
    total = await client.post.count(where={'title': 'kdbsajdh'})
    assert total == 0


@pytest.mark.asyncio
async def test_select(client: Client) -> None:
    """Selecting a field counts non-null values"""
    async with client.batch_() as batcher:
        batcher.post.create({'title': 'Foo', 'published': False})
        batcher.post.create({'title': 'Foo 2', 'published': False, 'desc': 'A'})

    count = await client.post.count(
        select={},
    )
    assert count == {'_all': 2}

    count = await client.post.count(
        select={
            'desc': True,
        },
    )
    assert count == {'desc': 1}

    count = await client.post.count(
        select={
            '_all': True,
            'desc': True,
        },
    )
    assert count == {'_all': 2, 'desc': 1}


@pytest.mark.asyncio
async def test_order_arg_deprecated(client: Client) -> None:
    """The order argument is deprecated"""
    with pytest.deprecated_call():
        await client.post.count(order={'desc': 'desc'})
