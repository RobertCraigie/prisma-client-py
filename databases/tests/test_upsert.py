import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_upsert(client: Prisma) -> None:
    """Upserting a non-existent and existing model updates fields"""
    user_id = 'asjdhsajd'
    assert await client.user.find_unique(where={'id': user_id}) is None

    user = await client.user.upsert(
        where={'id': user_id},
        data={
            'create': {'id': user_id, 'name': 'Robert'},
            'update': {'name': 'Robert'},
        },
    )
    assert user.id == user_id
    assert user.name == 'Robert'

    user = await client.user.upsert(
        where={'id': user_id},
        data={
            'create': {'id': user_id, 'name': 'Bob'},
            'update': {'name': 'Bob'},
        },
    )
    assert user.id == user_id
    assert user.name == 'Bob'

    assert await client.user.count() == 1
