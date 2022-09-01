from datetime import datetime
from prisma import Prisma


async def filtering(client: Prisma) -> None:
    # case: all valid filter fields
    await client.types.find_first(
        where={
            'datetime': datetime.now(),
        },
    )
    await client.types.find_first(
        where={
            'datetime': {
                'not': datetime.now(),
            },
        },
    )
    await client.types.find_first(
        where={
            'datetime': {
                'not': {
                    'not': {
                        'not': {
                            'not': {
                                'equals': datetime.now(),
                            },
                        },
                    },
                },
            },
        },
    )
    await client.types.find_first(
        where={
            'datetime': {
                'equals': datetime.now(),
                'in': [datetime.now(), datetime.utcnow()],
                'not_in': [datetime.now(), datetime.utcnow()],
                'lt': datetime.now(),
                'lte': datetime.now(),
                'gt': datetime.now(),
                'gte': datetime.now(),
                'not': {
                    'equals': datetime.now(),
                    'in': [datetime.now(), datetime.utcnow()],
                    'not_in': [datetime.now(), datetime.utcnow()],
                    'lt': datetime.now(),
                    'lte': datetime.now(),
                    'gt': datetime.now(),
                    'gte': datetime.now(),
                    'not': {
                        'equals': datetime.now(),
                    },
                },
            },
        },
    )

    # case: invalid types
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'datetime': 'foo',
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'datetime': {
                'equals': '1',
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[str | int]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'datetime': {
                'in': ['1', 2],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[int | str]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'datetime': {
                'not_in': [2, '3'],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, list[int]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'datetime': {
                'lt': [2],
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, tuple[Unknown, ...]]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'datetime': {
                'lte': tuple(),
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, str]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'datetime': {
                'gt': '1',
            },
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, dict[str, Prisma]]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'datetime': {
                'gte': client,
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
            'datetime': datetime.now(),
        },
    )

    # case: invalid types
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'datetime': [],  # E: Argument of type "dict[str, list[Any]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
        },
    )
    await client.types.update(
        where={
            'id': 1,
        },
        data={
            'datetime': {  # E: Argument of type "dict[str, dict[str, bool]]" cannot be assigned to parameter "data" of type "TypesUpdateInput" in function "update"
                'decrement': True,
            },
        },
    )
