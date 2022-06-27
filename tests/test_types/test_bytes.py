import pytest
from prisma import Prisma
from prisma.fields import Base64
from prisma.models import Types


@pytest.mark.asyncio
async def test_filtering(client: Prisma) -> None:
    """Finding records by a Bytes value"""
    async with client.batch_() as batcher:
        batcher.types.create({'bytes': Base64.encode(b'a')})
        batcher.types.create({'bytes': Base64.encode(b'b')})
        batcher.types.create({'bytes': Base64.encode(b'foo bar')})

    total = await client.types.count(
        where={
            'bytes': {
                'equals': Base64.encode(b'a'),
            },
        },
    )
    assert total == 1

    found = await client.types.find_first(
        where={
            'bytes': {
                'equals': Base64.encode(b'foo bar'),
            },
        },
    )
    assert found is not None
    assert found.bytes.decode() == b'foo bar'
    assert found.bytes.decode_str() == 'foo bar'

    found = await client.types.find_first(
        where={
            'bytes': {
                'not': Base64.encode(b'a'),
            },
        },
    )
    assert found is not None
    assert found.bytes.decode() == b'b'

    found = await client.types.find_first(
        where={
            'bytes': Base64.encode(b'a'),
        },
    )
    assert found is not None
    assert found.bytes.decode() == b'a'

    found = await client.types.find_first(
        where={
            'bytes': {
                'in': [Base64.encode(b'a'), Base64.encode(b'c')],
            }
        },
    )
    assert found is not None
    assert found.bytes.decode() == b'a'

    found = await client.types.find_first(
        where={
            'bytes': {
                'in': [Base64.encode(b'c')],
            },
        },
    )
    assert found is None

    found_list = await client.types.find_many(
        where={
            'bytes': {
                'not_in': [Base64.encode(b'a'), Base64.encode(b'c')],
            }
        },
    )
    found_values = {record.bytes.decode() for record in found_list}
    assert found_values == {b'b', b'foo bar'}


@pytest.mark.asyncio
async def test_json(client: Prisma) -> None:
    """Base64 fields can be serialised to and from JSON"""
    record = await client.types.create(
        data={
            'bytes': Base64.encode(b'foo'),
        },
    )
    model = Types.parse_raw(record.json())
    assert isinstance(model.bytes, Base64)
    assert model.bytes.decode() == b'foo'


@pytest.mark.asyncio
async def test_constructing(client: Prisma) -> None:
    """Base64 fields can be passed to the model constructor"""
    record = await client.types.create({})
    model = Types.parse_obj(
        {
            **record.dict(),
            'bytes': Base64.encode(b'foo'),
        },
    )
    assert model.bytes == Base64.encode(b'foo')


@pytest.mark.asyncio
async def test_filtering_nulls(client: Prisma) -> None:
    """None is a valid filter for nullable Bytes fields"""
    await client.types.create(
        {
            'string': 'a',
            'optional_bytes': None,
        },
    )
    await client.types.create(
        {
            'string': 'b',
            'optional_bytes': Base64.encode(b'foo'),
        },
    )
    await client.types.create(
        {
            'string': 'c',
            'optional_bytes': Base64.encode(b'bar'),
        },
    )

    found = await client.types.find_first(
        where={
            'NOT': [
                {
                    'optional_bytes': None,
                },
            ],
        },
        order={
            'string': 'asc',
        },
    )
    assert found is not None
    assert found.string == 'b'
    assert found.optional_bytes == Base64.encode(b'foo')

    count = await client.types.count(
        where={
            'optional_bytes': None,
        },
    )
    assert count == 1

    count = await client.types.count(
        where={
            'NOT': [
                {
                    'optional_bytes': None,
                },
            ],
        },
    )
    assert count == 2
