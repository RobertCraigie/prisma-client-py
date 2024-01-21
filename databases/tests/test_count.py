import pytest

from prisma import Prisma

# TODO: more tests


@pytest.mark.asyncio
async def test_count(client: Prisma) -> None:
    """Basic usage with a result"""
    await client.post.create({'title': 'post 1', 'published': False})
    assert await client.post.count() == 1


@pytest.mark.asyncio
async def test_count_no_results(client: Prisma) -> None:
    """No results returns 0"""
    total = await client.post.count(where={'title': 'kdbsajdh'})
    assert total == 0


@pytest.mark.asyncio
async def test_take(client: Prisma) -> None:
    """Take argument limits the maximum value"""
    async with client.batch_() as batcher:
        batcher.post.create({'title': 'Foo 1', 'published': False})
        batcher.post.create({'title': 'Foo 2', 'published': False})
        batcher.post.create({'title': 'Foo 3', 'published': False})

    total = await client.post.count(take=1)
    assert total == 1


@pytest.mark.asyncio
async def test_skip(client: Prisma) -> None:
    """Skip argument ignores the first N records"""
    async with client.batch_() as batcher:
        batcher.post.create({'title': 'Foo 1', 'published': False})
        batcher.post.create({'title': 'Foo 2', 'published': False})
        batcher.post.create({'title': 'Foo 3', 'published': False})

    total = await client.post.count(skip=1)
    assert total == 2


@pytest.mark.asyncio
async def test_select(client: Prisma) -> None:
    """Selecting a field counts non-null values"""
    async with client.batch_() as batcher:
        batcher.post.create({'title': 'Foo', 'published': False})
        batcher.post.create({'title': 'Foo 2', 'published': False, 'description': 'A'})

    count = await client.post.count(
        select={},
    )
    assert count == {'_all': 2}

    count = await client.post.count(
        select={
            'description': True,
        },
    )
    assert count == {'description': 1}

    count = await client.post.count(
        select={
            '_all': True,
            'description': True,
        },
    )
    assert count == {'_all': 2, 'description': 1}
