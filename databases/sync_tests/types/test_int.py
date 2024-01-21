import pytest

from prisma import Prisma
from prisma.errors import DataError

from ...utils import CURRENT_DATABASE


def test_filtering(client: Prisma) -> None:
    """Finding records by a an integer value"""
    with client.batch_() as batcher:
        for i in range(10):
            batcher.types.create({'integer': i + 1})

    total = client.types.count(where={'integer': {'gte': 5}})
    assert total == 6

    found = client.types.find_first(
        where={
            'integer': {
                'equals': 2,
            },
        },
    )
    assert found is not None
    assert found.integer == 2

    results = client.types.find_many(
        where={
            'integer': {
                'in': [1, 5, 7],
            },
        },
        order={
            'integer': 'asc',
        },
    )
    assert len(results) == 3
    assert results[0].integer == 1
    assert results[1].integer == 5
    assert results[2].integer == 7

    results = client.types.find_many(
        where={
            'integer': {
                'not_in': [1, 2, 3, 4, 6, 7, 8, 9],
            },
        },
        order={
            'integer': 'asc',
        },
    )
    assert len(results) == 2
    assert results[0].integer == 5
    assert results[1].integer == 10

    found = client.types.find_first(
        where={
            'integer': {
                'lt': 5,
            },
        },
        order={
            'integer': 'desc',
        },
    )
    assert found is not None
    assert found.integer == 4

    found = client.types.find_first(
        where={
            'integer': {
                'lte': 5,
            },
        },
        order={
            'integer': 'desc',
        },
    )
    assert found is not None
    assert found.integer == 5

    found = client.types.find_first(
        where={
            'integer': {
                'gt': 5,
            },
        },
        order={
            'integer': 'asc',
        },
    )
    assert found is not None
    assert found.integer == 6

    found = client.types.find_first(
        where={
            'integer': {
                'gte': 6,
            },
        },
        order={
            'integer': 'asc',
        },
    )
    assert found is not None
    assert found.integer == 6

    found = client.types.find_first(
        where={
            'integer': {
                'not': 1,
            },
        },
        order={'integer': 'asc'},
    )
    assert found is not None
    assert found.integer == 2


def test_atomic_update(client: Prisma) -> None:
    """Atomically updating an integer value"""
    model = client.types.create({'id': 1, 'integer': 1})
    assert model.integer == 1

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'integer': {'increment': 5},
        },
    )
    assert updated is not None
    assert updated.integer == 6

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'integer': {
                'set': 20,
            },
        },
    )
    assert updated is not None
    assert updated.integer == 20

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'integer': {
                'decrement': 5,
            },
        },
    )
    assert updated is not None
    assert updated.integer == 15

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'integer': {
                'multiply': 2,
            },
        },
    )
    assert updated is not None
    assert updated.integer == 30


@pytest.mark.skipif(
    CURRENT_DATABASE == 'cockroachdb',
    reason='https://github.com/prisma/prisma/issues/16511',
)
def test_atomic_update_divide(client: Prisma) -> None:
    """Atomically dividing an integer value"""
    model = client.types.create({'id': 1, 'integer': 30})
    assert model.integer == 30

    updated = client.types.update(
        where={
            'id': 1,
        },
        data={
            'integer': {
                'divide': 3,
            },
        },
    )
    assert updated is not None
    assert updated.integer == 10


def test_atomic_update_invalid_input(client: Prisma) -> None:
    """Integer atomic update only allows one field to be passed"""
    with pytest.raises(DataError) as exc:
        client.types.update(
            where={
                'id': 1,
            },
            data={
                'integer': {  # type: ignore
                    'divide': 1,
                    'multiply': 2,
                },
            },
        )

    message = exc.value.args[0]
    assert isinstance(message, str)
    assert 'Expected exactly one field to be present, got 2' in message


def test_filtering_nulls(client: Prisma) -> None:
    """None is a valid filter for nullable Int fields"""
    client.types.create(
        {
            'string': 'a',
            'optional_int': None,
        },
    )
    client.types.create(
        {
            'string': 'b',
            'optional_int': 1,
        },
    )
    client.types.create(
        {
            'string': 'c',
            'optional_int': 2,
        },
    )

    found = client.types.find_first(
        where={
            'NOT': [
                {
                    'optional_int': None,
                },
            ],
        },
        order={
            'string': 'asc',
        },
    )
    assert found is not None
    assert found.string == 'b'
    assert found.optional_int == 1

    count = client.types.count(
        where={
            'optional_int': None,
        },
    )
    assert count == 1

    count = client.types.count(
        where={
            'NOT': [
                {
                    'optional_int': None,
                },
            ],
        },
    )
    assert count == 2
