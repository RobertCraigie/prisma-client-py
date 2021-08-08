import pytest
from prisma import Client


# TODO: more tests


@pytest.mark.asyncio
async def test_count(client: Client) -> None:
    assert await client.post.count() == 0
    await client.post.create({'title': 'post 1', 'published': False})
    assert await client.post.count() == 1


@pytest.mark.asyncio
async def test_count_no_results(client: Client) -> None:
    total = await client.post.count(where={'title': 'kdbsajdh'})
    assert total == 0
