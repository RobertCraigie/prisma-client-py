import pytest
from prisma import Client


@pytest.mark.asyncio
async def test_find_first(client: Client) -> None:
    posts = [
        await client.post.create({'title': 'Test post 1', 'published': False}),
        await client.post.create({'title': 'Test post 2', 'published': False}),
        await client.post.create({'title': 'Test post 3', 'published': False}),
        await client.post.create({'title': 'Test post 4', 'published': True}),
        await client.post.create({'title': 'Test post 5', 'published': False}),
    ]

    post = await client.post.find_first({'where': {'published': True}})
    assert post is not None
    assert post.title == 'Test post 4'
    assert post.published is True

    post = await client.post.find_first({'where': {'title': {'contains': 'not found'}}})
    assert post is None
