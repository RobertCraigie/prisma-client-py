import pytest
from prisma import Client


@pytest.mark.asyncio
async def test_filtering(client: Client) -> None:
    """Finding records by a Boolean value"""
    async with client.batch_() as batcher:
        for i in range(10):
            batcher.types.create({'bool': i % 2 == 0})

    total = await client.types.count(where={'bool': {'equals': True}})
    assert total == 5

    found = await client.types.find_first(
        where={
            'bool': {
                'equals': False,
            },
        },
    )
    assert found is not None
    assert found.bool is False

    found = await client.types.find_first(
        where={
            'bool': {
                'not': True,
            },
        },
    )
    assert found is not None
    assert found.bool is False

    found = await client.types.find_first(
        where={
            'bool': {
                'not': False,
            },
        },
    )
    assert found is not None
    assert found.bool is True

    found = await client.types.find_first(
        where={
            'bool': False,
        },
    )
    assert found is not None
    assert found.bool is False
