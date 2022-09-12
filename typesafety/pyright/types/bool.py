from prisma import Prisma


async def filtering(client: Prisma) -> None:
    # case: all valid filter fields
    await client.types.find_first(
        where={
            'bool': True,
        },
    )
    await client.types.find_first(
        where={
            'bool': {
                'not': True,
            },
        },
    )
    await client.types.find_first(
        where={
            'bool': {
                'not': {
                    'not': {
                        'not': {
                            'not': {
                                'equals': True,
                            },
                        },
                    },
                },
            },
        },
    )
    await client.types.find_first(
        where={
            'bool': {
                'equals': False,
                'not': {
                    'equals': True,
                    'not': {
                        'equals': False,
                    },
                },
            },
        },
    )

    # case: invalid types
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'bool': 'foo',
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'bool': {
                'equals': '1',
            },
        },
    )

    # case: invalid field
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, bool]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'bool': {
                'foo': True,
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
            'bool': True,
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'bool': False,
        },
    )

    # case: invalid types
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'bool': [],  # E: Argument of type "dict[str, list[Any]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'bool': {  # E: Argument of type "dict[str, dict[str, bool]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'decrement': True,
            },
        },
    )
