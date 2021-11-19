from typing import Dict
from prisma import Json, JsonPath, Client


def raw() -> None:
    # case: valid
    Json(None)
    Json(True)
    Json(False)
    Json(1.3723)
    Json(56)
    Json('hello world')
    Json(['hello world'])
    Json(['foo', 'bar', 'baz'])
    Json({'foo': 10})
    Json({'foo': {'bar': {'baz': 1}}})

    # case: no other arguments
    Json('bar', 'foo')  # E: Expected 1 positional argument
    Json('foo', item=1)  # E: No parameter named "item"

    # case: invalid recursive type
    Json(
        {  # E: Argument of type "dict[str, dict[str, dict[str, Type[Json]]]]" cannot be assigned to parameter "data" of type "Serializable" in function "__init__"
            'foo': {
                'bar': {
                    'baz': Json,
                },
            },
        },
    )


def keys() -> None:
    # case: valid
    Json.keys(item=None)
    Json.keys(item=True)
    Json.keys(item=False)
    Json.keys(item=1.3723)
    Json.keys(item=56)
    Json.keys(item='hello world')
    Json.keys(item=['hello world'])
    Json.keys(item=['foo', 'bar', 'baz'])
    Json.keys(item={'foo': 10})
    Json.keys(item={'foo': {'bar': {'baz': 1}}})

    # case: unpacking inferred
    kwargs1 = {'hello': 'world'}
    Json.keys(**kwargs1)

    # case: unpacking explicit
    kwargs2: Dict[str, str] = {'hello': 'world'}
    Json.keys(**kwargs2)

    # case: invalid recursive type
    Json.keys(
        item={  # E: Argument of type "dict[str, dict[str, dict[str, Type[Json]]]]" cannot be assigned to parameter "item" of type "Serializable" in function "keys"
            'foo': {
                'bar': {
                    'baz': Json,
                },
            },
        },
    )

    # case: invalid key types
    Json.keys(item={})


async def allowed_operations(client: Client) -> None:
    model = await client.types.create(data={'json_obj': Json('foo')})
    obj = model.json_obj
    assert obj is not None

    # case: dict is expected
    assert obj['foo'] is True

    # case: list is expected
    assert obj[0] == 'foo'
    assert obj[1:3] == [1, 2]

    # case: string is expected
    assert obj[0] == 'f'
    assert obj[1:3] == 'er'


async def narrowing_types(client: Client) -> None:
    model = await client.types.create(data={'json_obj': Json('foo')})
    obj = model.json_obj
    assert obj is not None
    reveal_type(obj)  # T: Json

    # case: dict
    if isinstance(obj, dict):
        reveal_type(obj)  # T: <subclass of Json and dict>
        obj.update(name='foo')

    # case: list
    elif isinstance(obj, list):
        reveal_type(obj)  # T: <subclass of Json and list>
        obj.append('foo')


async def client_api(client: Client) -> None:
    # case: cannot pass Json to string field
    await client.types.create(
        data={  # E: Argument of type "dict[str, Json]" cannot be assigned to parameter "data" of type "TypesCreateInput" in function "create"
            'string': Json('wow'),
        },
    )

    # case: narrowing type
    model = await client.types.create(data={'json_obj': Json('1')})
    assert isinstance(model.json_obj, int)
    number = model.json_obj + 1
    reveal_type(number)  # T: int


async def preview_feature_filtering(client: Client) -> None:
    # case: path required
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'json_obj': {
                'string_contains': 'foo',
            },
        },
    )

    # case: Json is distinct from str
    await client.types.find_first(
        where={
            'json_obj': {  # E: Argument of type "dict[str, dict[str, Any]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
                'path': JsonPath('foo'),
                'string_contains': Json('wow'),
            },
        },
    )

    # case: valid
    await client.types.find_first(
        where={
            'json_obj': {
                'path': JsonPath('foo', 'bar'),
                'string_contains': 'foo',
            },
        },
    )

    # TODO: all fields
