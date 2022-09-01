from prisma import Prisma


async def filtering(client: Prisma) -> None:
    # case: all valid filter fields
    await client.types.find_first(
        where={
            'string': 'foo',
        },
    )
    await client.types.find_first(
        where={
            'string': {
                'not': 'foo',
            },
        },
    )
    await client.types.find_first(
        where={
            'string': {
                'not': {
                    'not': {
                        'not': {
                            'not': {
                                'equals': 'wow',
                            },
                        },
                    },
                },
            },
        },
    )
    await client.types.find_first(
        where={
            'string': {
                'equals': 'foo',
                'in': ['bar', 'baz'],
                'not_in': ['foo', 'thing'],
                'lt': 'prisma',
                'lte': 'prisma 2',
                'gt': 'python',
                'gte': 'wow',
                'contains': 'foo',
                'startswith': 'bar',
                'endswith': 'baz',
                'mode': 'insensitive',
                'not': {
                    'equals': 'foo',
                    'in': ['one', 'two'],
                    'not_in': ['three', 'four'],
                    'lt': 'five',
                    'lte': 'six',
                    'gt': 'seven',
                    'gte': 'eight',
                    'contains': 'foo',
                    'startswith': 'bar',
                    'endswith': 'baz',
                    'mode': 'default',
                    'not': {
                        'equals': 'ten',
                    },
                },
            },
        },
    )

    # case: invalid types
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, int]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': 1,
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'equals': 1,
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[str | int]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'in': ['1', 2],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[int | str]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'not_in': [2, '3'],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[int]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'lt': [2],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, tuple[Unknown, ...]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'lte': tuple(),
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[Unknown]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'gt': list(),
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, Prisma]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'gte': client,
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'contains': 1,
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'startswith': 1,
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, int]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'endswith': 1,
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'string': {
                'mode': 'foo',
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
            'string': 'foo',
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'string': '\n'.join('foo,three'.split(',')),
        },
    )

    # case: invalid types
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'string': [],  # E: Argument of type "dict[str, list[Any]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'string': {  # E: Argument of type "dict[str, dict[str, bool]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'decrement': True,
            },
        },
    )
