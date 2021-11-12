import pytest
from prisma import Client
from prisma.fields import Base64


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
