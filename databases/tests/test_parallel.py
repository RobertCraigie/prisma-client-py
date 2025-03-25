import pytest
import asyncio

from prisma import Prisma


@pytest.mark.asyncio
async def test_count(client: Prisma) -> None:
    """Basic usage with a result"""
    await client.post.create({'title': 'post 1', 'published': False})
    promises = [client.post.count() for _ in range(1000)]
    results = await asyncio.gather(*promises)
    assert all(result == 1 for result in results)
