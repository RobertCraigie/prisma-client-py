import pytest
from prisma import Prisma


@pytest.mark.asyncio
async def test_create_many(client: Prisma) -> None:
    """Creating multiple records in a single batch"""
    async with client.batch_() as batcher:
        batcher.user.create({'name': 'Robert'})
        batcher.user.create({'name': 'Tegan'})

    assert await client.user.count() == 2
