import pytest
from prisma import Client


@pytest.mark.asyncio
async def test_find_first(client: Client) -> None:
    """Skips multiple non-matching records"""
    posts = [
        await client.post.create({'title': 'Test post 1', 'published': False}),
        await client.post.create({'title': 'Test post 2', 'published': False}),
        await client.post.create({'title': 'Test post 3', 'published': False}),
        await client.post.create({'title': 'Test post 4', 'published': True}),
        await client.post.create({'title': 'Test post 5', 'published': False}),
        await client.post.create({'title': 'Test post 6', 'published': True}),
    ]

    post = await client.post.find_first(where={'published': True})
    assert post is not None
    assert post.id == posts[3].id
    assert post.title == 'Test post 4'
    assert post.published is True

    post = await client.post.find_first(where={'title': {'contains': 'not found'}})
    assert post is None

    post = await client.post.find_first(where={'published': True}, skip=1)
    assert post is not None
    assert post.id == posts[5].id
    assert post.title == 'Test post 6'
    assert post.published is True
