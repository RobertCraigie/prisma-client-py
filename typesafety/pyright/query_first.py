from prisma import Prisma
from prisma.models import User


async def main(client: Prisma) -> None:
    user = await client.query_first('', model=User)
    reveal_type(user)  # T: User | None
    assert user is not None
    reveal_type(user)  # T: User
    reveal_type(user.id)  # T: str

    user.foo  # E: Cannot access member "foo" for type "User"

    result = await client.query_first('')
    reveal_type(result)  # T: dict[str, Any]

    query = 'safe StringLiteral query'
    await client.query_first(query, model=User)

    query = str('unsafe str query')
    await client.query_first(
        query,  # E: Argument of type "str" cannot be assigned to parameter "query" of type "LiteralString" in function "query_first"
        model=User,
    )
