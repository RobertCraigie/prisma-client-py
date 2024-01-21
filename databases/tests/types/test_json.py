import pytest
from dirty_equals import IsPartialDict

from prisma import Json, Prisma
from prisma.models import Types
from prisma._compat import PYDANTIC_V2, model_json_schema


@pytest.mark.asyncio
async def test_create(client: Prisma) -> None:
    """Creating a model with Json data"""
    model = await client.types.create(
        data={
            'json_obj': Json.keys(country='Scotland'),
        },
    )
    assert model.json_obj == {'country': 'Scotland'}

    model = await client.types.create(
        data={
            'json_obj': Json.keys(countries=['Scotland', 'United Kingdom']),
        },
    )
    assert model.json_obj == {'countries': ['Scotland', 'United Kingdom']}

    model = await client.types.create(
        data={
            'json_obj': Json(['Scotland']),
        },
    )
    assert model.json_obj == ['Scotland']

    model = await client.types.create(
        data={
            'json_obj': Json('Scotland'),
        },
    )
    assert model.json_obj == 'Scotland'

    model = await client.types.create(
        data={
            'json_obj': Json(1),
        },
    )
    assert model.json_obj == 1

    model = await client.types.create(
        data={
            'json_obj': Json(None),
        },
    )
    assert model.json_obj is None

    model = await client.types.create(
        data={
            'json_obj': Json({'hello': None}),
        },
    )
    assert model.json_obj == {'hello': None}

    model = await client.types.create(
        data={
            'json_obj': Json(19.3273823),
        },
    )
    assert model.json_obj == 19.3273823


@pytest.mark.asyncio
async def test_keys(client: Prisma) -> None:
    """Handling of non-string keys"""
    model = await client.types.create(
        data={
            'json_obj': Json({None: 'hello'}),
        },
    )
    assert model.json_obj is not None
    assert model.json_obj == {'null': 'hello'}
    assert model.json_obj['null'] == 'hello'

    model = await client.types.create(
        data={
            'json_obj': Json({True: 2}),
        },
    )
    assert model.json_obj is not None
    assert model.json_obj == {'true': 2}
    assert model.json_obj['true'] == 2

    model = await client.types.create(
        data={
            'json_obj': Json({1: 2}),
        },
    )
    assert model.json_obj is not None
    assert model.json_obj == {'1': 2}
    assert model.json_obj['1'] == 2

    model = await client.types.create(
        data={
            'json_obj': Json({3.1415: [1, 2]}),
        },
    )
    assert model.json_obj is not None
    assert model.json_obj == {'3.1415': [1, 2]}
    assert model.json_obj['3.1415'] == [1, 2]


@pytest.mark.asyncio
async def test_base_filtering(client: Prisma) -> None:
    """Searching for records by Json values without the preview feature enabled"""
    found = await client.types.find_first(
        where={
            'json_obj': {
                'equals': Json.keys(country='Scotland'),
            },
        },
    )
    assert found is None

    model = await client.types.create(
        data={
            'json_obj': Json.keys(country='Scotland'),
        },
    )
    assert model.json_obj == {'country': 'Scotland'}

    found = await client.types.find_first(
        where={
            'json_obj': {
                'equals': Json.keys(country='Scotland'),
            },
        },
    )
    assert found is not None
    assert found.id == model.id
    assert found.json_obj == {'country': 'Scotland'}

    found = await client.types.find_first(
        where={
            'json_obj': {
                'not': Json.keys(country='Scotland'),
            },
        },
    )
    assert found is None

    found = await client.types.find_first(
        where={
            'json_obj': {
                'not': Json.keys(countries=['Scotland']),
            },
        },
    )
    assert found is not None
    assert found.id == model.id
    assert found.json_obj == {'country': 'Scotland'}


@pytest.mark.asyncio
async def test_unserializable_type(client: Prisma) -> None:
    """Error is raised when an unserializable type is encountered"""
    with pytest.raises(TypeError) as exc:
        await client.types.create(
            data={
                'json_obj': Json.keys(foo=Prisma),  # type: ignore
            },
        )

    assert exc.match(r'Type <class \'prisma.client.Prisma\'> not serializable')


def test_json_schema() -> None:
    """Ensure a JSON Schema definition can be created"""
    if PYDANTIC_V2:
        assert model_json_schema(Types) == IsPartialDict(
            properties=IsPartialDict(
                {
                    'json_obj': {
                        'anyOf': [
                            {
                                'contentMediaType': 'application/json',
                                'contentSchema': {},
                                'type': 'string',
                            },
                            {'type': 'null'},
                        ],
                        'default': None,
                        'title': 'Json Obj',
                    }
                }
            ),
        )
    else:
        assert model_json_schema(Types) == IsPartialDict(
            properties=IsPartialDict(
                {
                    'json_obj': {
                        'title': 'Json Obj',
                        'type': 'string',
                        'format': 'json-string',
                    }
                }
            ),
        )
