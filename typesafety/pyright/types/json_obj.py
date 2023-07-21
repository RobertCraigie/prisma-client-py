from typing import Dict
from prisma import Json, Prisma


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
    # TODO: these error messages are weird...
    Json(
        'bar',  # E: Argument of type "Literal['bar']" cannot be assigned to parameter "object" of type "ReadableBuffer" in function "__new__"
        'foo',
    )
    Json(  # E: No overloads for "__new__" match the provided arguments
        'foo',
        item=1,
    )

    # case: invalid recursive type
    Json(
        {  # E: Argument of type "dict[str, dict[str, dict[str, type[Json]]]]" cannot be assigned to parameter "data" of type "Serializable" in function "__init__"
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
        item={  # E: Argument of type "dict[str, dict[str, dict[str, type[Json]]]]" cannot be assigned to parameter "item" of type "Serializable" in function "keys"
            'foo': {
                'bar': {
                    'baz': Json,
                },
            },
        },
    )

    # case: invalid key types
    Json.keys(item={})


async def allowed_operations(client: Prisma) -> None:
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


async def narrowing_types(client: Prisma) -> None:
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


async def client_api(client: Prisma) -> None:
    # case: cannot pass Json to string field
    # TODO: this should error
    await client.types.create(
        data={
            'string': Json('wow'),
        },
    )

    # case: narrowing type
    model = await client.types.create(data={'json_obj': Json('1')})
    assert isinstance(model.json_obj, int)
    number = model.json_obj + 1
    reveal_type(number)  # T: int
