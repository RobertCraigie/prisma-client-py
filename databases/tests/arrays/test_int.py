import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_updating_ints(client: Prisma) -> None:
    """Updating an Int[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'ints': [1, 2, 3],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'ints': {
                'set': [5],
            },
        },
    )
    assert model is not None
    assert model.ints == [5]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'ints': [6],
        },
    )
    assert model is not None
    assert model.ints == [6]


@pytest.mark.asyncio
async def test_filtering_ints(client: Prisma) -> None:
    """Searching for records by an Int[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'ints': [],
            },
        )
        batcher.lists.create(
            data={
                'ints': [1, 2, 3],
            },
        )

    model = await client.lists.find_first(
        where={
            'ints': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.ints == []

    model = await client.lists.find_first(
        where={
            'ints': {
                'equals': [1, 2, 3],
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'ints': {
                'has': 1,
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'ints': {
                'has': 4,
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'ints': {
                'has_some': [2, 3, 4],
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'ints': {
                'has_every': [2, 3, 4],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'ints': {
                'has_every': [1, 2],
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3]

    count = await client.lists.count(
        where={
            'ints': {
                'is_empty': True,
            },
        },
    )
    assert count == 1
