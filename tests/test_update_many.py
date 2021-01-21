import pytest
from prisma import Client


@pytest.mark.asyncio
async def test_update_many(client: Client) -> None:
    posts = [
        await client.post.create({'title': 'Test post 1', 'published': False}),
        await client.post.create({'title': 'Test post 2', 'published': False}),
    ]
    count = await client.post.update_many(
        where={'published': False}, data={'published': True}
    )
    assert count == 2

    post = await client.post.find_unique(where={'id': posts[0].id})
    assert post is not None
    assert post.published is True

    count = await client.post.update_many(
        where={'published': False}, data={'published': True}
    )
    assert count == 0

    count = await client.post.update_many(
        where={'id': posts[0].id}, data={'published': False}
    )
    assert count == 1

    post = await client.post.find_unique(where={'id': posts[0].id})
    assert post is not None
    assert post.published is False

    count = await client.post.update_many(
        where={'published': False}, data={'views': 10}
    )
    assert count == 1

    post = await client.post.find_unique(where={'id': posts[0].id})
    assert post is not None
    assert post.views == 10

    count = await client.post.update_many(
        where={'id': posts[0].id}, data={'id': 'sdhajd'}
    )
    assert count == 1

    post = await client.post.find_unique(where={'id': 'sdhajd'})
    assert post is not None

    post = await client.post.find_unique(where={'id': posts[0].id})
    assert post is None
