from decimal import Decimal
from prisma import Prisma


async def filtering(client: Prisma) -> None:
    # case: valid filter fields
    await client.types.find_first(
        where={
            'decimal': Decimal('1'),
        },
    )
    await client.types.find_first(
        where={
            'decimal': {
                'equals': Decimal(1),
            },
        },
    )
    await client.types.find_first(
        where={
            'decimal': {
                'not': Decimal('1.2345'),
            },
        },
    )
    await client.types.find_first(
        where={
            'decimal': {
                'not': {
                    'equals': Decimal('1'),
                },
            },
        },
    )

    # case: invalid types
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, bytes]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'decimal': b'foo',
        },
    )
    await client.types.find_first(
        where={  # E: Argument of type "dict[str, bytes]" cannot be assigned to parameter "where" of type "TypesWhereInput | None" in function "find_first"
            'decimal': b'foo',
        },
    )
