from prisma import Prisma


async def filtering(client: Prisma) -> None:
    # case: all valid filter fields
    await client.types.find_first(
        where={
            'integer': 237283,
        },
    )
    await client.types.find_first(
        where={
            'integer': {
                'not': 173283,
            },
        },
    )
    await client.types.find_first(
        where={
            'integer': {
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
            'integer': {
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
            'integer': 'foo',
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'integer': {
                'equals': '1',
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[str | int]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'integer': {
                'in': ['1', 2],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[int | str]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'integer': {
                'not_in': [2, '3'],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[int]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'integer': {
                'lt': [2],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, tuple[_T_co@tuple]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'integer': {
                'lte': tuple(),
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'integer': {
                'gt': '1',
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, Prisma]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'integer': {
                'gte': client,
            },
        },
    )
    await client.types.find_first(
        where={
            'integer': {
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
            'integer': 290521015266836500,
        },
    )

    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'integer': {
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
            'integer': {
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
            'integer': {
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
            'integer': {
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
            'integer': {
                'decrement': 15,
            },
        },
    )

    # case: invalid field
    await client.types.update(
        where={
            'id': 1,
        },
        data={  # E: # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
            'integer': {
                'foo': 15,
            },
        },
    )

    # case: invalid types
    await client.types.update(
        where={
            'id': 1,
        },
        data={  # E: Argument of type "dict[str, list[Any]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
            'integer': [],
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
            'integer': {
                'decrement': 'a',
            },
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={  # E: Argument of type "dict[str, dict[str, Prisma]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
            'integer': {
                'increment': client,
            },
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={  # E: Argument of type "dict[str, dict[str, set[Unknown]]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
            'integer': {
                'multiply': set(),
            },
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={  # E: Argument of type "dict[str, dict[str, set[Unknown]]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
            'integer': {
                'divide': set(),
            },
        },
    )

    # case: too many arguments
    await client.types.update(
        where={
            'id': 1,
        },
        data={  # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
            'integer': {
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
        data={  # E: Argument of type "dict[str, dict[Any, Any]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
            'integer': {},
        },
    )
