import pytest

from prisma import Base64, Prisma
from prisma.models import Lists
from prisma._compat import model_dict, model_parse


@pytest.mark.asyncio
async def test_updating_bytes(client: Prisma) -> None:
    """Updating a Bytes[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'bytes': [Base64.encode(b'foo'), Base64.encode(b'bar')],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bytes': {
                'set': [Base64.encode(b'd')],
            },
        },
    )
    assert model is not None
    assert model.bytes == [Base64.encode(b'd')]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bytes': [Base64.encode(b'e')],
        },
    )
    assert model is not None
    assert model.bytes == [Base64.encode(b'e')]


@pytest.mark.asyncio
async def test_filtering_bytes(client: Prisma) -> None:
    """Searching for records by a Bytes[] value"""
    expected_objects = [Base64.encode(b'foo'), Base64.encode(b'bar')]
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'bytes': [],
            },
        )
        batcher.lists.create(
            data={
                'bytes': expected_objects,
            },
        )

    model = await client.lists.find_first(
        where={
            'bytes': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.bytes == []

    model = await client.lists.find_first(
        where={
            'bytes': {
                'equals': expected_objects,
            },
        },
    )
    assert model is not None
    assert model.bytes == expected_objects

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has': Base64.encode(b'foo'),
            },
        },
    )
    assert model is not None
    assert model.bytes == expected_objects

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has': Base64.encode(b'baz'),
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has_some': [*expected_objects, Base64.encode(b'fjhf')],
            },
        },
    )
    assert model is not None
    assert model.bytes == expected_objects

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has_every': [*expected_objects, Base64.encode(b'prisma')],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has_every': [*expected_objects[:2]],
            },
        },
    )
    assert model is not None
    assert model.bytes == expected_objects

    count = await client.lists.count(
        where={
            'bytes': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_bytes_constructing(client: Prisma) -> None:
    """A list of Base64 fields can be passed to the model constructor"""
    record = await client.lists.create({})
    model = model_parse(
        Lists,
        {
            **model_dict(record),
            'bytes': [
                Base64.encode(b'foo'),
                Base64.encode(b'bar'),
            ],
        },
    )
    assert model.bytes == [Base64.encode(b'foo'), Base64.encode(b'bar')]
