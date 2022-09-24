from datetime import datetime
from prisma import Prisma, Base64, Json
from prisma.enums import Role


# NOTE: we only test for invalid cases here as there is already extensive tests
# for valid cases in `tests/integrations/postgresql/tests/test_arrays.py`


async def filtering(client: Prisma) -> None:
    # case: multiple arguments not allowed
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'strings': {
                'equals': None,
                'has': 'a',
            },
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, Base64 | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'bytes': {
                'equals': None,
                'has': Base64.encode(b'foo'),
            },
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, datetime | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'dates': {
                'equals': None,
                'has': datetime.utcnow(),
            },
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, bool | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'bools': {
                'equals': None,
                'has': True,
            },
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, int | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'ints': {
                'equals': None,
                'has': 2,
            },
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, float | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'floats': {
                'equals': None,
                'has': 10.4,
            },
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, int | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'bigints': {
                'equals': None,
                'has': 237263876387263823,
            },
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, Json | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'json_objects': {
                'equals': None,
                'has': Json('foo'),
            },
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, Role | None]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'roles': {
                'equals': None,
                'has': Role.ADMIN,
            },
        },
    )

    # NOTE: after this we just test one type for simplicity's sake and it is
    # incredibly unlikely for there to be any deviance in behaviour between types

    # case: invalid equals
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, int]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'strings': 1,
        },
    )
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'strings': {
                'equals': 'foo',
            },
        },
    )

    # case: invalid has
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[str]]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'strings': {
                'has': ['foo'],
            },
        },
    )

    # case: invalid has_every
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'strings': {
                'has_every': 'foo',
            },
        },
    )

    # case: invalid has_some
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'strings': {
                'has_some': 'bar',
            },
        },
    )

    # case: invalid is_empty
    await client.lists.find_first(
        where={  # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "where" of type "ListsWhereInput | None" in function "find_first"
            'strings': {
                'is_empty': 1,
            },
        },
    )


async def updating(client: Prisma) -> None:
    # case: invalid set
    await client.lists.update(
        where={
            'id': '',
        },
        data={
            'strings': 'foo',  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "data" of type "ListsUpdateInput" in function "update"
        },
    )
    await client.lists.update(
        where={
            'id': '',
        },
        data={
            'strings': {  # E: Argument of type "dict[str, dict[str, tuple[Literal['foo'], Literal['bar']]]]" cannot be assigned to parameter "data" of type "ListsUpdateInput" in function "update"
                'set': ('foo', 'bar'),
            },
        },
    )

    # case: invalid push
    await client.lists.update(
        where={
            'id': '',
        },
        data={
            'strings': {  # E: Argument of type "dict[str, dict[str, tuple[Literal['foo'], Literal['bar']]]]" cannot be assigned to parameter "data" of type "ListsUpdateInput" in function "update"
                'push': ('foo', 'bar'),
            },
        },
    )


async def models(client: Prisma) -> None:
    model = await client.lists.find_first()
    assert model is not None
    reveal_type(model.ints)  # T: List[int]
    reveal_type(model.roles)  # T: List[Role]
    reveal_type(model.bytes)  # T: List[Base64]
    reveal_type(model.dates)  # T: List[datetime]
    reveal_type(model.bools)  # T: List[bool]
    reveal_type(model.floats)  # T: List[float]
    reveal_type(model.bigints)  # T: List[int]
    reveal_type(model.strings)  # T: List[str]
    reveal_type(model.json_objects)  # T: List[Json]
