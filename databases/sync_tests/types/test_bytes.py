from typing import List

from pydantic import BaseModel

from prisma import Prisma
from prisma.fields import Base64
from prisma.models import Types
from prisma._compat import (
    model_dict,
    model_json,
    model_parse,
    model_parse_json,
)


def test_filtering(client: Prisma) -> None:
    """Finding records by a Bytes value"""
    with client.batch_() as batcher:
        batcher.types.create({'bytes': Base64.encode(b'a')})
        batcher.types.create({'bytes': Base64.encode(b'b')})
        batcher.types.create({'bytes': Base64.encode(b'foo bar')})

    total = client.types.count(
        where={
            'bytes': {
                'equals': Base64.encode(b'a'),
            },
        },
    )
    assert total == 1

    found = client.types.find_first(
        where={
            'bytes': {
                'equals': Base64.encode(b'foo bar'),
            },
        },
    )
    assert found is not None
    assert found.bytes.decode() == b'foo bar'
    assert found.bytes.decode_str() == 'foo bar'

    found = client.types.find_first(
        where={
            'bytes': {
                'not': Base64.encode(b'a'),
            },
        },
    )
    assert found is not None
    assert found.bytes.decode() == b'b'

    found = client.types.find_first(
        where={
            'bytes': Base64.encode(b'a'),
        },
    )
    assert found is not None
    assert found.bytes.decode() == b'a'

    found = client.types.find_first(
        where={
            'bytes': {
                'in': [Base64.encode(b'a'), Base64.encode(b'c')],
            }
        },
    )
    assert found is not None
    assert found.bytes.decode() == b'a'

    found = client.types.find_first(
        where={
            'bytes': {
                'in': [Base64.encode(b'c')],
            },
        },
    )
    assert found is None

    found_list = client.types.find_many(
        where={
            'bytes': {
                'not_in': [Base64.encode(b'a'), Base64.encode(b'c')],
            }
        },
    )
    found_values = {record.bytes.decode() for record in found_list}
    assert found_values == {b'b', b'foo bar'}


def test_json(client: Prisma) -> None:
    """Base64 fields can be serialised to and from JSON"""
    record = client.types.create(
        data={
            'bytes': Base64.encode(b'foo'),
        },
    )
    model = model_parse_json(Types, model_json(record, exclude={'json_obj'}))
    assert isinstance(model.bytes, Base64)
    assert model.bytes.decode() == b'foo'


def test_constructing(client: Prisma) -> None:
    """Base64 fields can be passed to the model constructor"""
    record = client.types.create({})
    model = model_parse(
        Types,
        {
            **model_dict(record, exclude={'json_obj'}),
            'bytes': Base64.encode(b'foo'),
        },
    )
    assert model.bytes == Base64.encode(b'foo')


def test_filtering_nulls(client: Prisma) -> None:
    """None is a valid filter for nullable Bytes fields"""
    client.types.create(
        {
            'string': 'a',
            'optional_bytes': None,
        },
    )
    client.types.create(
        {
            'string': 'b',
            'optional_bytes': Base64.encode(b'foo'),
        },
    )
    client.types.create(
        {
            'string': 'c',
            'optional_bytes': Base64.encode(b'bar'),
        },
    )

    found = client.types.find_first(
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

    count = client.types.count(
        where={
            'optional_bytes': None,
        },
    )
    assert count == 1

    count = client.types.count(
        where={
            'NOT': [
                {
                    'optional_bytes': None,
                },
            ],
        },
    )
    assert count == 2


class Base64Model(BaseModel):
    value: Base64
    array: List[Base64]


def test_pydantic_conversion() -> None:
    """Raw inputs are converted to Base64 objects at the Pydantic level"""
    record = model_parse(Base64Model, {'value': 'foo', 'array': []})
    assert isinstance(record.value, Base64)
    assert record.value._raw == b'foo'
    assert record.array == []

    record = model_parse(
        Base64Model,
        {
            'value': Base64.encode(b'foo'),
            'array': ['foo', b'bar', Base64.encode(b'baz')],
        },
    )
    assert isinstance(record.value, Base64)
    assert record.value.decode() == b'foo'
    assert len(record.array) == 3
    assert record.array[0]._raw == b'foo'
    assert record.array[1]._raw == b'bar'
    assert record.array[2].decode_str() == 'baz'
