import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_updating_floats(client: Prisma) -> None:
    """Updating a Float[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'floats': [3.4, 6.8, 12.4],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'floats': {
                'set': [99999.999],
            },
        },
    )
    assert model is not None
    assert model.floats == [99999.999]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'floats': [80],
        },
    )
    assert model is not None
    assert model.floats == [80]


@pytest.mark.asyncio
async def test_filtering_floats(client: Prisma) -> None:
    """Searching for records by a Float[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'floats': [],
            },
        )
        batcher.lists.create(
            data={
                'floats': [1.3, 2.6, 3.9],
            },
        )

    model = await client.lists.find_first(
        where={
            'floats': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.floats == []

    model = await client.lists.find_first(
        where={
            'floats': {
                'equals': [1.3, 2.6, 3.9],
            },
        },
    )
    assert model is not None
    assert model.floats == [1.3, 2.6, 3.9]

    model = await client.lists.find_first(
        where={
            'floats': {
                'has': 2.6,
            },
        },
    )
    assert model is not None
    assert model.floats == [1.3, 2.6, 3.9]

    model = await client.lists.find_first(
        where={
            'floats': {
                'has': 4.0,
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'floats': {
                'has_some': [2.6, 3.9, 4.5],
            },
        },
    )
    assert model is not None
    assert model.floats == [1.3, 2.6, 3.9]

    model = await client.lists.find_first(
        where={
            'floats': {
                'has_every': [2.6, 3.9, 4.5],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'floats': {
                'has_every': [2.6, 3.9],
            },
        },
    )
    assert model is not None
    assert model.floats == [1.3, 2.6, 3.9]

    count = await client.lists.count(
        where={
            'floats': {
                'is_empty': True,
            },
        },
    )
    assert count == 1
