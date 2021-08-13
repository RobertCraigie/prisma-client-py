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
