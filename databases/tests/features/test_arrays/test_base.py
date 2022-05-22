import pytest
from prisma import Prisma


# TODO: add these tests for all types


@pytest.mark.asyncio
async def test_order_by(client: Prisma) -> None:
    """Results can be ordered by a String[] field"""
    total = await client.lists.create_many(
        [
            {'id': 'a', 'strings': ['a', 'b']},
            {'id': 'b', 'strings': ['c']},
        ],
    )
    assert total == 2

    models = await client.lists.find_many(order={'strings': 'desc'})
    assert len(models) == 2
    assert models[0].id == 'b'
    assert models[1].id == 'a'

    models = await client.lists.find_many(order={'strings': 'asc'})
    assert len(models) == 2
    assert models[0].id == 'a'
    assert models[1].id == 'b'


@pytest.mark.asyncio
async def test_update_many(client: Prisma) -> None:
    """Updating many String[] values"""
    result = await client.lists.create_many(
        [
            {'id': 'a', 'strings': ['foo']},
            {'id': 'b', 'strings': ['bar']},
        ]
    )
    assert result == 2

    result = await client.lists.update_many(
        where={},
        data={
            'strings': {
                'set': ['foo'],
            },
        },
    )
    assert result == 2

    model = await client.lists.find_unique(
        where={
            'id': 'a',
        },
    )
    assert model is not None
    assert model.strings == ['foo']
