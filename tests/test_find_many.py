import pytest
from prisma import Client


@pytest.mark.asyncio
async def test_find_many(client: Client) -> None:
    posts = [
        await client.post.create({'title': 'Test post 1', 'published': False}),
        await client.post.create({'title': 'Test post 2', 'published': False}),
    ]
    found = await client.post.find_many(where={'title': 'Test post 1'})
    assert len(found) == 1
    assert found[0].id == posts[0].id

    posts = await client.post.find_many(
        where={'OR': [{'title': 'Test post 1'}, {'title': 'Test post 2'}]}
    )
    assert len(posts) == 2

    posts = await client.post.find_many(where={'title': {'contains': 'Test post'}})
    assert len(posts) == 2

    posts = await client.post.find_many(where={'title': {'startswith': 'Test post'}})
    assert len(posts) == 2

    posts = await client.post.find_many(where={'title': {'not_in': ['Test post 1']}})
    assert len(posts) == 1
    assert posts[0].title == 'Test post 2'

    posts = await client.post.find_many(where={'title': {'equals': 'Test post 2'}})
    assert len(posts) == 1
    assert posts[0].title == 'Test post 2'

    posts = await client.post.find_many(where={'title': 'Test post 2'})
    assert len(posts) == 1
    assert posts[0].title == 'Test post 2'

    posts = await client.post.find_many(order={'title': 'desc'})
    assert len(posts) == 2
    assert posts[0].title == 'Test post 2'
    assert posts[1].title == 'Test post 1'

    posts = await client.post.find_many(order={'title': 'asc'})
    assert len(posts) == 2
    assert posts[0].title == 'Test post 1'
    assert posts[1].title == 'Test post 2'
