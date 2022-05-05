import pytest
from prisma import Prisma


# TODO: more tests


@pytest.mark.asyncio
async def test_delete_many(client: Prisma) -> None:
    """Standard usage"""
    posts = [
        await client.post.create({'title': 'Foo post', 'published': False}),
        await client.post.create({'title': 'Bar post', 'published': False}),
    ]
    count = await client.post.delete_many()
    assert count >= 1

    for post in posts:
        assert await client.post.find_unique(where={'id': post.id}) is None


@pytest.mark.asyncio
async def test_delete_many_where(client: Prisma) -> None:
    """delete_many with a where clause"""
    await client.post.create({'title': 'Foo post', 'published': False})
    await client.post.create({'title': 'Bar post', 'published': False})

    count = await client.post.delete_many(
        where={'ANY': [{'title': 'Foo post'}, {'title': 'Bar post'}]}
    )
    assert count == 2
