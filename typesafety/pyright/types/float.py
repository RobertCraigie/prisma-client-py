from prisma import Prisma


async def filtering(client: Prisma) -> None:
    # case: all valid filter fields
    await client.types.find_first(
        where={
            'float_': 237283,
        },
    )
    await client.types.find_first(
        where={
            'float_': {
                'not': 173283,
            },
        },
    )
    await client.types.find_first(
        where={
            'float_': {
                'not': {
                    'not': {
                        'not': {
                            'not': {
                                'equals': 1,
                            },
                        },
                    },
                },
            },
        },
    )
    await client.types.find_first(
        where={
            'float_': {
                'equals': 2,
                'in': [2, 3, 4],
                'not_in': [5, 6, 7],
                'lt': 3,
                'lte': 2,
                'gt': 1,
                'gte': 2,
                'not': {
                    'equals': 2,
                    'in': [2, 3, 4],
                    'not_in': [5, 6, 7],
                    'lt': 3,
                    'lte': 2,
                    'gt': 1,
                    'gte': 2,
                    'not': {
                        'equals': 3,
                    },
                },
            },
        },
    )

    # case: invalid types
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'float_': 'foo',
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'float_': {
                'equals': '1',
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[str | int]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'float_': {
                'in': ['1', 2],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[int | str]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'float_': {
                'not_in': [2, '3'],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[int]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'float_': {
                'lt': [2],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, tuple[Unknown, ...]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'float_': {
                'lte': tuple(),
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'float_': {
                'gt': '1',
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, Prisma]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'float_': {
                'gte': client,
            },
        },
    )
    await client.types.find_first(
        where={
            'float_': {
                'not': {
                    'equals': 5,
                },
            },
        },
    )


async def updating(client: Prisma) -> None:
    # case: setting
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': 290521015266836500,
        },
    )

    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'set': 540521015266836500,
            },
        },
    )

    # case: multiplying
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'multiply': 10,
            },
        },
    )

    # case: dividing
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'divide': 2,
            },
        },
    )

    # case: adding
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'increment': 15,
            },
        },
    )

    # case: subtracting
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {
                'decrement': 15,
            },
        },
    )

    # case: invalid field
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {  # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'foo': 15,
            },
        },
    )

    # case: invalid types
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': [],  # E: Argument of type "dict[str, list[Any]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'decrement': 'a',
            },
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {  # E: Argument of type "dict[str, dict[str, Prisma]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'increment': client,
            },
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {  # E: Argument of type "dict[str, dict[str, set[Unknown]]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'multiply': set(),
            },
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {  # E: Argument of type "dict[str, dict[str, set[Unknown]]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'divide': set(),
            },
        },
    )

    # case: too many arguments
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {  # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'divide': 5,
                'multiply': 2,
            },
        },
    )

    # case: too few arguments
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'float_': {},  # E: Argument of type "dict[str, dict[Any, Any]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
        },
    )
