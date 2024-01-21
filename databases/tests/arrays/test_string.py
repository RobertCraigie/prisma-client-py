import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_updating_strings(client: Prisma) -> None:
    """Updating a String[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'strings': ['a', 'b', 'c'],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'strings': {
                'set': ['e'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['e']

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'strings': ['f'],
        },
    )
    assert model is not None
    assert model.strings == ['f']


@pytest.mark.asyncio
async def test_filtering_strings(client: Prisma) -> None:
    """Searching for records by a String[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'strings': [],
            },
        )
        batcher.lists.create(
            data={
                'strings': ['a', 'b', 'c'],
            },
        )

    model = await client.lists.find_first(
        where={
            'strings': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.strings == []  # TODO: document this behaviour

    model = await client.lists.find_first(
        where={
            'strings': {
                'equals': ['a', 'b', 'c'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    model = await client.lists.find_first(
        where={
            'strings': {
                'has': 'a',
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    model = await client.lists.find_first(
        where={
            'strings': {
                'has': 'd',
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'strings': {
                'has_some': ['b', 'c'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    model = await client.lists.find_first(
        where={
            'strings': {
                'has_every': ['b', 'c', 'd'],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'strings': {
                'has_every': ['a', 'b'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    count = await client.lists.count(
        where={
            'strings': {
                'is_empty': True,
            },
        },
    )
    assert count == 1
