from prisma import Prisma


async def main(client: Prisma) -> None:
    query = 'safe StringLiteral query'
    await client.execute_raw(query)

    query = str('unsafe str query')
    await client.execute_raw(
        query  # E: Argument of type "str" cannot be assigned to parameter "query" of type "LiteralString" in function "execute_raw"
    )
