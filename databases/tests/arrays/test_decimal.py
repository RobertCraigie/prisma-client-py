from decimal import Decimal

import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_updating_decimal(client: Prisma) -> None:
    """Updating a Decimal[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'decimals': [Decimal('22.99'), Decimal('30.01')],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'decimals': {
                'set': [Decimal('3')],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal('3')]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'decimals': [Decimal('7')],
        },
    )
    assert model is not None
    assert model.decimals == [Decimal('7')]


@pytest.mark.asyncio
async def test_filtering_decimal(client: Prisma) -> None:
    """Searching for records by a Decimal[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'decimals': [],
            },
        )
        batcher.lists.create(
            data={
                'decimals': [Decimal('1'), Decimal('2')],
            },
        )

    model = await client.lists.find_first(
        where={
            'decimals': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.decimals == []

    model = await client.lists.find_first(
        where={
            'decimals': {
                'equals': [Decimal('1'), Decimal('2')],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal(1), Decimal(2)]

    model = await client.lists.find_first(
        where={
            'decimals': {
                'has': Decimal('1'),
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal(1), Decimal(2)]

    model = await client.lists.find_first(
        where={
            'decimals': {
                'has': Decimal(3),
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'decimals': {
                'has_some': [Decimal(1), Decimal(3)],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal(1), Decimal(2)]

    model = await client.lists.find_first(
        where={
            'decimals': {
                'has_every': [Decimal(1), Decimal(2), Decimal(3)],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'decimals': {
                'has_every': [Decimal(1)],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal(1), Decimal(2)]

    count = await client.lists.count(
        where={
            'decimals': {
                'is_empty': True,
            },
        },
    )
    assert count == 1
