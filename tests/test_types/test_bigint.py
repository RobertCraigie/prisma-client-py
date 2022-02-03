import pytest
from prisma import Prisma
from prisma.errors import DataError


@pytest.mark.asyncio
async def test_filtering(client: Prisma) -> None:
    """Finding records by a BigInt value"""
    async with client.batch_() as batcher:
        for i in range(10):
            batcher.types.create({'bigint': i + 1})

    total = await client.types.count(where={'bigint': {'gte': 5}})
    assert total == 6

    found = await client.types.find_first(
        where={
            'bigint': {
                'equals': 2,
            },
        },
    )
    assert found is not None
    assert found.bigint == 2

    results = await client.types.find_many(
        where={
            'bigint': {
                'in': [1, 5, 7],
            },
        },
        order={
            'bigint': 'asc',
        },
    )
    assert len(results) == 3
    assert results[0].bigint == 1
    assert results[1].bigint == 5
    assert results[2].bigint == 7

    results = await client.types.find_many(
        where={
            'bigint': {
                'not_in': [1, 2, 3, 4, 6, 7, 8, 9],
            },
        },
        order={
            'bigint': 'asc',
        },
    )
    assert len(results) == 2
    assert results[0].bigint == 5
    assert results[1].bigint == 10

    found = await client.types.find_first(
        where={
            'bigint': {
                'lt': 5,
            },
        },
        order={
            'bigint': 'desc',
        },
    )
    assert found is not None
    assert found.bigint == 4

    found = await client.types.find_first(
        where={
            'bigint': {
                'lte': 5,
            },
        },
        order={
            'bigint': 'desc',
        },
    )
    assert found is not None
    assert found.bigint == 5

    found = await client.types.find_first(
        where={
            'bigint': {
                'gt': 5,
            },
        },
        order={
            'bigint': 'asc',
        },
    )
    assert found is not None
    assert found.bigint == 6

    found = await client.types.find_first(
        where={
            'bigint': {
                'gte': 6,
            },
        },
        order={
            'bigint': 'asc',
        },
    )
    assert found is not None
    assert found.bigint == 6

    found = await client.types.find_first(
        where={
            'bigint': {
                'not': 1,
            },
        },
        order={'bigint': 'asc'},
    )
    assert found is not None
    assert found.bigint == 2


@pytest.mark.asyncio
async def test_atomic_update(client: Prisma) -> None:
    """Atomically updating a BigInt value"""
    model = await client.types.create({'id': 1, 'bigint': 1})
    assert model.bigint == 1

    updated = await client.types.update(
        where={
            'id': 1,
        },
        data={
            'bigint': {'increment': 5},
        },
    )
    assert updated is not None
    assert updated.bigint == 6

    updated = await client.types.update(
        where={
            'id': 1,
        },
        data={
            'bigint': {
                'set': 20,
            },
        },
    )
    assert updated is not None
    assert updated.bigint == 20

    updated = await client.types.update(
        where={
            'id': 1,
        },
        data={
            'bigint': {
                'decrement': 5,
            },
        },
    )
    assert updated is not None
    assert updated.bigint == 15

    updated = await client.types.update(
        where={
            'id': 1,
        },
        data={
            'bigint': {
                'multiply': 2,
            },
        },
    )
    assert updated is not None
    assert updated.bigint == 30

    updated = await client.types.update(
        where={
            'id': 1,
        },
        data={
            'bigint': {
                'divide': 3,
            },
        },
    )
    assert updated is not None
    assert updated.bigint == 10


@pytest.mark.asyncio
async def test_atomic_update_invalid_input(client: Prisma) -> None:
    """BigInt atomic update only allows one field to be passed"""
    with pytest.raises(DataError) as exc:
        await client.types.update(
            where={
                'id': 1,
            },
            data={  # pyright: reportGeneralTypeIssues=false
                'bigint': {  # type: ignore
                    'divide': 1,
                    'multiply': 2,
                },
            },
        )

    message = exc.value.args[0]
    assert isinstance(message, str)
    assert 'Expected exactly one field to be present, got 2' in message
