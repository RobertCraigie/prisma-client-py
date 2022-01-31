import pytest
from prisma import Client
from prisma.fields import Base64
from prisma.models import Types


@pytest.mark.asyncio
async def test_filtering(client: Client) -> None:
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


@pytest.mark.asyncio
async def test_json(client: Client) -> None:
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
async def test_constructing(client: Client) -> None:
    """Base64 fields can be passed to the model constructor"""
    record = await client.types.create({})
    model = Types.parse_obj(
        {
            **record.dict(),
            'bytes': Base64.encode(b'foo'),
        },
    )
    assert model.bytes == Base64.encode(b'foo')
