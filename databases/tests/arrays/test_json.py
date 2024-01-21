import pytest

from prisma import Json, Prisma


@pytest.mark.asyncio
async def test_updating_json(client: Prisma) -> None:
    """Updating a Json[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'json_objects': [Json('foo'), Json(['foo', 'bar'])],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'json_objects': {
                'set': [Json.keys(hello=123)],
            },
        },
    )
    assert model is not None
    assert model.json_objects == [{'hello': 123}]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'json_objects': [Json.keys(world=None)],
        },
    )
    assert model is not None
    assert model.json_objects == [{'world': None}]


@pytest.mark.asyncio
async def test_filtering_json(client: Prisma) -> None:
    """Searching for records by a Json[] value"""
    expected_raw: list[object] = [[], {'country': 'Scotland'}]
    expected_objects = [Json([]), Json.keys(country='Scotland')]

    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'json_objects': [],
            },
        )
        batcher.lists.create(
            data={
                'json_objects': expected_objects,
            },
        )

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.json_objects == []

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'equals': expected_objects,
            },
        },
    )
    assert model is not None
    assert model.json_objects == expected_raw

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has': Json([]),
            },
        },
    )
    assert model is not None
    assert model.json_objects == expected_raw

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has': Json(['foo']),
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has_some': [*expected_objects, Json(['foo'])],
            },
        },
    )
    assert model is not None
    assert model.json_objects == expected_raw

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has_every': [*expected_objects, Json(['foo'])],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has_every': [*expected_objects[:2]],
            },
        },
    )
    assert model is not None
    assert model.json_objects == expected_raw

    count = await client.lists.count(
        where={
            'json_objects': {
                'is_empty': True,
            },
        },
    )
    assert count == 1
