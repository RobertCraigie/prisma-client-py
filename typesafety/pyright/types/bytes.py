from prisma import Prisma, Base64


async def filtering(client: Prisma) -> None:
    # case: all valid filter fields
    await client.types.find_first(
        where={
            'bytes': Base64.encode(b'foo'),
        },
    )
    await client.types.find_first(
        where={
            'bytes': {
                'equals': Base64.encode(b'a'),
            },
        },
    )
    await client.types.find_first(
        where={
            'bytes': {
                'not': Base64.encode(b'a'),
            },
        },
    )
    await client.types.find_first(
        where={
            'bytes': {
                'not': {
                    'equals': Base64.encode(b'a'),
                },
            },
        },
    )

    # case: invalid types
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, bytes]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'bytes': b'foo',
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, bytes]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'bytes': b'foo',
        },
    )
