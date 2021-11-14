from typing import Iterator
from decimal import Decimal, getcontext
import pytest
from prisma import Client


@pytest.fixture(autouse=True)
def configure_decimal_module() -> Iterator[None]:
    prev = getcontext().prec

    try:
        getcontext().prec = 28
        yield
    finally:
        getcontext().prec = prev


@pytest.mark.asyncio
async def test_serialising(client: Client) -> None:
    """Decimal values of any precision are correctly serialised / deserialised"""
    model = await client.types.create(
        data={
            'decimal': Decimal(1),
        },
    )
    assert model.decimal == Decimal(1)

    value = Decimal(1) / Decimal(7)
    model = await client.types.create(
        data={
            'decimal': value,
        },
    )
    print(value)
    assert value == model.decimal
    assert str(model.decimal) == '0.1428571428571428571428571429'

    print(model.json(indent=2))
    assert False


@pytest.mark.asyncio
async def test_filtering(client: Client) -> None:
    """Finding records by a Decimal value"""
    """
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
    """
