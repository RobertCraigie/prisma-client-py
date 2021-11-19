import pytest
from prisma import Client, Json
from prisma.fields import JsonPath


@pytest.mark.asyncio
async def test_create(client: Client) -> None:
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
async def test_keys(client: Client) -> None:
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
async def test_base_filtering(client: Client) -> None:
    """Searching for records by Json values without the preview feature enabled"""
    found = await client.types.find_first(
        where={
            'json_obj': {
                'equals': Json.keys(country='Scotland'),
            },
        },
    )
    assert found is None

    model = await client.types.create(data={'json_obj': Json.keys(country='Scotland')})
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


"""
TODO: test

'lt': 'fields.Json',
'lte': 'fields.Json',
'gt': 'fields.Json',
'gte': 'fields.Json',
'path': 'fields.JsonPath',
'string_contains': str,
'string_starts_with': str,
'string_ends_with': str,
'array_contains': 'fields.Json',
'array_starts_with': 'fields.Json',
'array_ends_with': 'fields.Json',
"""

# TODO: rename
@pytest.mark.asyncio
async def test_preview_filtering(client: Client) -> None:
    model = await client.types.create(
        data={
            'json_obj': Json(
                {
                    'favourites': {
                        'catBreed': 'Turkish van',
                        'dogBreed': 'Rottweiler',
                        'sanctuaries': ['RSPCA', 'Alley Cat Allies'],
                        'treats': [
                            {'name': 'Dreamies', 'manufacturer': 'Mars Inc'},
                            {'name': 'Treatos', 'manufacturer': 'The Dog People'},
                        ],
                    },
                    'fostered': {
                        'cats': ['Bob', 'Alice', 'Svetlana the Magnificent', 'Queenie']
                    },
                    'owned': {
                        'cats': ['Elliott'],
                    },
                    'stats': {
                        'owned': 1,
                    },
                },
            )
        }
    )

    found = await client.types.find_first(
        where={
            'json_obj': {
                'path': JsonPath('stats', 'owned'),
                'lt': Json(2),
            },
        },
    )
    assert found is not None
    assert found.id == model.id

    import datetime

    for v in [None, True, 1, '1', datetime.datetime.utcnow(), [2, 3, 4]]:
        found = await client.types.find_first(
            where={
                'json_obj': {
                    'path': JsonPath('stats', 'owned'),
                    'lt': Json(v),
                },
            },
        )
        print(found)
        # assert found is not None
        # assert found.id == model.id

    found = await client.types.find_first(
        where={
            'json_obj': {
                'path': JsonPath('favourites', 'dogBreed'),
                'equals': Json('Rottweiler'),
            }
        }
    )
    assert found is not None
    assert found.id == model.id

    found = await client.types.find_first(
        where={
            'json_obj': {
                'path': JsonPath('favourites', 'dogBreed'),
                'string_contains': 'Rott',
            },
        },
    )
    assert found is not None
    assert found.id == model.id

    assert False


@pytest.mark.asyncio
async def test_unserializable_type(client: Client) -> None:
    """Error is raised when an unserializable type is encountered"""
    with pytest.raises(TypeError) as exc:
        await client.types.create(
            data={
                'json_obj': Json.keys(foo=Client),  # type: ignore
            },
        )

    assert exc.match(r'Type <class \'prisma.client.Client\'> not serializable')
