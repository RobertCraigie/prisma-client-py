from prisma import Prisma


async def main(client: Prisma) -> None:
    # case: missing arguments
    await client.user.find_unique()  # E: Argument missing for parameter "where"
    await client.user.find_unique(
        where={}  # E: Argument of type "dict[Any, Any]" cannot be assigned to parameter "where" of type "UserWhereUniqueInput" in function "find_unique"
    )

    # case: nullable field is not nullable in filter
    await client.user.find_unique(
        where={  # E: Argument of type "dict[str, None]" cannot be assigned to parameter "where" of type "UserWhereUniqueInput" in function "find_unique"
            'email': None,
        },
    )

    # case: multiple fields not allowed
    await client.user.find_unique(
        where={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "where" of type "UserWhereUniqueInput" in function "find_unique"
            'id': 'foo',
            'email': 'foo',
        },
    )

    # case: invalid types
    await client.user.find_unique(
        where={  # E: Argument of type "dict[str, int]" cannot be assigned to parameter "where" of type "UserWhereUniqueInput" in function "find_unique"
            'email': 1,
        },
    )

    # case: valid
    await client.user.find_unique(
        where={
            'email': 'foo',
        },
    )
    await client.user.find_unique(
        where={
            'id': 'foo',
        },
    )
