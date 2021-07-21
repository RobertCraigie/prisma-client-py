from prisma import Client
from prisma.models import User


async def main(client: Client) -> None:
    users = await client.query_raw('', model=User)
    reveal_type(users)  # T: List[User]
    reveal_type(users[0])  # T: User
    reveal_type(users[0].id)  # T: str

    users[0].foo  # E: Cannot access member "foo" for type "User"

    result = await client.query_raw('')
    reveal_type(result)  # T: Any
