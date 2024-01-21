import pytest

from prisma import Prisma
from prisma.errors import DataError


def test_filtering(client: Prisma) -> None:
    """Finding records by a a float value"""
    with client.batch_() as batcher:
        for i in range(10):
            batcher.types.create({'float_': i + 1})

    total = client.types.count(where={'float_': {'gte': 5}})
    assert total == 6

    found = client.types.find_first(
        where={
            'float_': {
                'equals': 2,
            },
        },
    )
    assert found is not None
    assert found.float_ == 2

    results = client.types.find_many(
        where={
            'float_': {
                'in': [1, 5, 7],
            },
        },
        order={
            'float_': 'asc',
        },
    )
    assert len(results) == 3
    assert results[0].float_ == 1
    assert results[1].float_ == 5
    assert results[2].float_ == 7

    results = client.types.find_many(
        where={
            'float_': {
                'not_in': [1, 2, 3, 4, 6, 7, 8, 9],
            },
        },
        order={
            'float_': 'asc',
        },
    )
    assert len(results) == 2
    assert results[0].float_ == 5
    assert results[1].float_ == 10

    found = client.types.find_first(
        where={
            'float_': {
                'lt': 5,
            },
        },
        order={
            'float_': 'desc',
        },
    )
    assert found is not None
    assert found.float_ == 4

    found = client.types.find_first(
        where={
            'float_': {
                'lte': 5,
            },
        },
        order={
            'float_': 'desc',
        },
    )
    assert found is not None
    assert found.float_ == 5

    found = client.types.find_first(
        where={
            'float_': {
                'gt': 5,
            },
        },
        order={
            'float_': 'asc',
        },
    )
    assert found is not None
    assert found.float_ == 6

    found = client.types.find_first(
        where={
            'float_': {
                'gte': 6,
            },
        },
        order={
            'float_': 'asc',
        },
    )
    assert found is not None
    assert found.float_ == 6

    found = client.types.find_first(
        where={
            'float_': {
                'not': 1,
            },
        },
        order={'float_': 'asc'},
    )
    assert found is not None
    assert found.float_ == 2


def test_atomic_update(client: Prisma) -> None:
    """Atomically updating a float value"""
    model = client.types.create({'id': 1, 'float_': 1})
    assert model.float_ == 1

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {'increment': 5},
        },
    )
    assert updated is not None
    assert updated.float_ == 6

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'set': 20,
            },
        },
    )
    assert updated is not None
    assert updated.float_ == 20

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'decrement': 5,
            },
        },
    )
    assert updated is not None
    assert updated.float_ == 15

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'multiply': 2,
            },
        },
    )
    assert updated is not None
    assert updated.float_ == 30

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'divide': 3,
            },
        },
    )
    assert updated is not None
    assert updated.float_ == 10


def test_atomic_update_invalid_input(client: Prisma) -> None:
    """Float atomic update only allows one field to be passed"""
    with pytest.raises(DataError) as exc:
        client.types.update(
            where={
                'id': 1,
            },
            data={
                'float_': {  # type: ignore
                    'divide': 1,
                    'multiply': 2,
                },
            },
        )

    message = exc.value.args[0]
    assert isinstance(message, str)
    assert 'Expected exactly one field to be present, got 2' in message


def test_filtering_nulls(client: Prisma) -> None:
    """None is a valid filter for nullable Float fields"""
    client.types.create(
        {
            'string': 'a',
            'optional_float': None,
        },
    )
    client.types.create(
        {
            'string': 'b',
            'optional_float': 1.2,
        },
    )
    client.types.create(
        {
            'string': 'c',
            'optional_float': 5,
        },
    )

    found = client.types.find_first(
        where={
            'NOT': [
                {
                    'optional_float': None,
                },
            ],
        },
        order={
            'string': 'asc',
        },
    )
    assert found is not None
    assert found.string == 'b'
    assert found.optional_float == 1.2

    count = client.types.count(
        where={
            'optional_float': None,
        },
    )
    assert count == 1

    count = client.types.count(
        where={
            'NOT': [
                {
                    'optional_float': None,
                },
            ],
        },
    )
    assert count == 2
