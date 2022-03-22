from decimal import Decimal, getcontext

import pytest
from prisma import Prisma


@pytest.mark.asyncio
async def test_serialising(client: Prisma) -> None:
    """Decimal values of any precision are correctly serialised / deserialised"""
    model = await client.types.create(
        data={
            'decimal': Decimal(1),
        },
    )
    assert model.decimal == Decimal(1)

    getcontext().prec = 16

    value = Decimal(1) / Decimal(7)
    model = await client.types.create(
        data={
            'decimal': value,
        },
    )
    assert value == model.decimal
    assert str(model.decimal) == '0.1428571428571429'


@pytest.mark.asyncio
async def test_filtering(client: Prisma) -> None:
    """Finding records by a Decimal value"""
    async with client.batch_() as batcher:
        batcher.types.create({'decimal': Decimal(1)})
        batcher.types.create({'decimal': Decimal(2.1234)})
        batcher.types.create({'decimal': Decimal(3)})

    total = await client.types.count(
        where={
            'decimal': Decimal(1),
        },
    )
    assert total == 1

    found = await client.types.find_first(
        where={
            'decimal': {
                'equals': Decimal(2.1234),
            },
        },
    )
    assert found is not None
    assert str(found.decimal) == '2.1234'

    results = await client.types.find_many(
        where={
            'decimal': {
                'not_in': [Decimal(1), Decimal(3)],
            },
        },
    )
    assert len(results) == 1
    assert results[0].decimal == Decimal('2.1234')

    results = await client.types.find_many(
        where={
            'decimal': {
                'lt': Decimal(2),
            },
        },
    )
    assert len(results) == 1
    assert results[0].decimal == Decimal(1)

    found = await client.types.find_first(
        where={
            'decimal': {
                'lt': Decimal(1),
            },
        },
    )
    assert found is None

    results = await client.types.find_many(
        where={
            'decimal': {
                'lte': Decimal(3),
            },
        },
    )
    assert len(results) == 3

    found = await client.types.find_first(
        where={
            'decimal': {
                'lte': Decimal(1),
            },
        },
    )
    assert found is not None
    assert found.decimal == Decimal(1)

    found = await client.types.find_first(
        where={
            'decimal': {
                'lte': Decimal('0.99999'),
            },
        },
    )
    assert found is None

    found = await client.types.find_first(
        where={
            'decimal': {
                'gt': Decimal('0.99999'),
            },
        },
    )
    assert found is not None
    assert found.decimal == Decimal(1)

    found = await client.types.find_first(
        where={
            'decimal': {
                'gt': Decimal('4'),
            },
        },
    )
    assert found is None

    found = await client.types.find_first(
        where={
            'decimal': {
                'gte': Decimal('1'),
            },
        },
    )
    assert found is not None
    assert found.decimal == Decimal('1')

    found = await client.types.find_first(
        where={
            'decimal': {
                'gte': Decimal('4'),
            },
        },
    )
    assert found is None

    results = await client.types.find_many(
        where={
            'decimal': {
                'in': [Decimal(3), Decimal(1), Decimal(2)],
            },
        },
        order={
            'decimal': 'asc',
        },
    )
    assert len(results) == 2
    assert results[0].decimal == Decimal(1)
    assert results[1].decimal == Decimal(3)

    found = await client.types.find_first(
        where={
            'decimal': {
                'not': Decimal('1'),
            },
        },
        order={
            'decimal': 'asc',
        },
    )
    assert found is not None
    assert found.decimal == Decimal('2.1234')

    found = await client.types.find_first(
        where={
            'decimal': {
                'not': {'equals': Decimal('1')},
            },
        },
        order={
            'decimal': 'asc',
        },
    )
    assert found is not None
    assert found.decimal == Decimal('2.1234')
