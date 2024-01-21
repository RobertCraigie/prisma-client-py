from decimal import Decimal, getcontext

import pytest
from dirty_equals import IsPartialDict

from prisma import Prisma
from prisma.models import Types
from prisma._compat import PYDANTIC_V2, model_json_schema

DEFAULT_PRECISION = getcontext().prec


@pytest.fixture(autouse=True)
def setup_decimal_module() -> None:
    # ensure that any modifications to the decimal precision
    # are not leaked between tests
    getcontext().prec = DEFAULT_PRECISION


@pytest.mark.asyncio
async def test_serialising(client: Prisma) -> None:
    """Decimal values of any precision are correctly serialised / deserialised"""
    model = await client.types.create(
        data={
            'decimal_': Decimal(1),
        },
    )
    assert model.decimal_ == Decimal(1)

    getcontext().prec = 16

    value = Decimal(1) / Decimal(7)
    model = await client.types.create(
        data={
            'decimal_': value,
        },
    )
    assert value == model.decimal_
    assert str(model.decimal_) == '0.1428571428571429'


# TODO: split up this test into multiple tests


@pytest.mark.asyncio
async def test_filtering(client: Prisma) -> None:
    """Finding records by a Decimal value"""
    async with client.batch_() as batcher:
        batcher.types.create({'decimal_': Decimal(1)})
        batcher.types.create({'decimal_': Decimal('2.1234')})
        batcher.types.create({'decimal_': Decimal(3)})

    total = await client.types.count(
        where={
            'decimal_': Decimal(1),
        },
    )
    assert total == 1

    found = await client.types.find_first(
        where={
            'decimal_': {
                'equals': Decimal('2.1234'),
            },
        },
    )
    assert found is not None
    assert str(found.decimal_) == '2.1234'

    results = await client.types.find_many(
        where={
            'decimal_': {
                'not_in': [Decimal(1), Decimal(3)],
            },
        },
    )
    assert len(results) == 1
    assert results[0].decimal_ == Decimal('2.1234')

    results = await client.types.find_many(
        where={
            'decimal_': {
                'lt': Decimal(2),
            },
        },
    )
    assert len(results) == 1
    assert results[0].decimal_ == Decimal(1)

    found = await client.types.find_first(
        where={
            'decimal_': {
                'lt': Decimal(1),
            },
        },
    )
    assert found is None

    results = await client.types.find_many(
        where={
            'decimal_': {
                'lte': Decimal(3),
            },
        },
    )
    assert len(results) == 3

    found = await client.types.find_first(
        where={
            'decimal_': {
                'lte': Decimal(1),
            },
        },
    )
    assert found is not None
    assert found.decimal_ == Decimal(1)

    found = await client.types.find_first(
        where={
            'decimal_': {
                'lte': Decimal('0.99999'),
            },
        },
    )
    assert found is None

    found = await client.types.find_first(
        where={
            'decimal_': {
                'gt': Decimal('0.99999'),
            },
        },
    )
    assert found is not None
    assert found.decimal_ == Decimal(1)

    found = await client.types.find_first(
        where={
            'decimal_': {
                'gt': Decimal('4'),
            },
        },
    )
    assert found is None

    found = await client.types.find_first(
        where={
            'decimal_': {
                'gte': Decimal('1'),
            },
        },
    )
    assert found is not None
    assert found.decimal_ == Decimal('1')

    found = await client.types.find_first(
        where={
            'decimal_': {
                'gte': Decimal('4'),
            },
        },
    )
    assert found is None

    results = await client.types.find_many(
        where={
            'decimal_': {
                'in': [Decimal(3), Decimal(1), Decimal(2)],
            },
        },
        order={
            'decimal_': 'asc',
        },
    )
    assert len(results) == 2
    assert results[0].decimal_ == Decimal(1)
    assert results[1].decimal_ == Decimal(3)

    found = await client.types.find_first(
        where={
            'decimal_': {
                'not': Decimal('1'),
            },
        },
        order={
            'decimal_': 'asc',
        },
    )
    assert found is not None
    assert found.decimal_ == Decimal('2.1234')

    found = await client.types.find_first(
        where={
            'decimal_': {
                'not': {'equals': Decimal('1')},
            },
        },
        order={
            'decimal_': 'asc',
        },
    )
    assert found is not None
    assert found.decimal_ == Decimal('2.1234')


@pytest.mark.asyncio
async def test_filtering_nulls(client: Prisma) -> None:
    """None is a valid filter for nullable Decimal fields"""
    await client.types.create(
        {
            'string': 'a',
            'optional_decimal': None,
        },
    )
    await client.types.create(
        {
            'string': 'b',
            'optional_decimal': Decimal('3'),
        },
    )
    await client.types.create(
        {
            'string': 'c',
            'optional_decimal': Decimal('4'),
        },
    )

    found = await client.types.find_first(
        where={
            'NOT': [
                {
                    'optional_decimal': None,
                },
            ],
        },
        order={
            'string': 'asc',
        },
    )
    assert found is not None
    assert found.string == 'b'
    assert found.optional_decimal == Decimal('3')

    count = await client.types.count(
        where={
            'optional_decimal': None,
        },
    )
    assert count == 1

    count = await client.types.count(
        where={
            'NOT': [
                {
                    'optional_decimal': None,
                },
            ],
        },
    )
    assert count == 2


def test_json_schema() -> None:
    """Ensure a JSON Schema definition can be created"""
    if PYDANTIC_V2:
        assert model_json_schema(Types) == IsPartialDict(
            properties=IsPartialDict(
                {
                    'decimal_': {
                        'title': 'Decimal ',
                        'anyOf': [{'type': 'number'}, {'type': 'string'}],
                    },
                    'optional_decimal': {
                        'title': 'Optional Decimal',
                        'anyOf': [
                            {'type': 'number'},
                            {'type': 'string'},
                            {'type': 'null'},
                        ],
                        'default': None,
                    },
                }
            )
        )
    else:
        assert model_json_schema(Types) == IsPartialDict(
            properties=IsPartialDict(
                {
                    'decimal_': {
                        'title': 'Decimal ',
                        'type': 'number',
                    },
                    'optional_decimal': {
                        'title': 'Optional Decimal',
                        'type': 'number',
                    },
                }
            )
        )
