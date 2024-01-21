import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_updating_boolean(client: Prisma) -> None:
    """Updating a Boolean[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'bools': [False, True],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bools': {
                'set': [False],
            },
        },
    )
    assert model is not None
    assert model.bools == [False]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bools': [True],
        },
    )
    assert model is not None
    assert model.bools == [True]


@pytest.mark.asyncio
async def test_filtering_bools(client: Prisma) -> None:
    """Searching for records by a Boolean[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'bools': [],
            },
        )
        batcher.lists.create(
            data={
                'bools': [False, True],
            },
        )

    model = await client.lists.find_first(
        where={
            'bools': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.bools == []

    model = await client.lists.find_first(
        where={
            'bools': {
                'equals': [],
            },
        },
    )
    assert model is not None
    assert model.bools == []

    model = await client.lists.find_first(
        where={
            'bools': {
                'equals': [False, True],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    model = await client.lists.find_first(
        where={
            'bools': {
                'has': True,
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    model = await client.lists.find_first(
        where={
            'bools': {
                'has_some': [True],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    model = await client.lists.find_first(
        where={
            'bools': {
                'has_every': [False, True, False, True],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    model = await client.lists.find_first(
        where={
            'bools': {
                'has_every': [False, True],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    count = await client.lists.count(
        where={
            'bools': {
                'is_empty': True,
            },
        },
    )
    assert count == 1
