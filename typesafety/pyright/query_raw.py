from prisma import Prisma
from prisma.models import User


async def main(client: Prisma) -> None:
    users = await client.query_raw('', model=User)
    reveal_type(users)  # T: List[User]
    reveal_type(users[0])  # T: User
    reveal_type(users[0].id)  # T: str

    users[0].foo  # E: Cannot access member "foo" for type "User"

    result = await client.query_raw('')
    reveal_type(result)  # T: List[dict[str, Any]]

    query = 'safe StringLiteral query'
    await client.query_raw(query, model=User)

    query = str('unsafe str query')
    await client.query_raw(
        query,  # E: Argument of type "str" cannot be assigned to parameter "query" of type "LiteralString" in function "query_raw"
        model=User,
    )
