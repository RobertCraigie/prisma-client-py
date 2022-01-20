from prisma import Client
from prisma.models import User


async def main(client: Client) -> None:
    user = await client.user.find_unique(where={'id': '1'}, include={'posts': True})
    reveal_type(user)  # T: User | None
    assert user is not None

    for _ in user.posts:  # E: Object of type "None" cannot be used as iterable value
        ...

    assert user.posts is not None
    for post in user.posts:
        ...

    reveal_type(user.posts)  # T: List[Post]


async def order_by(client: Client, user: User) -> None:
    # case: 1-M valid
    await client.user.find_unique(
        where={
            'id': user.id,
        },
        include={
            'posts': {
                'order_by': {
                    'published': 'asc',
                },
            },
        },
    )

    # case: 1-M invalid field
    await client.user.find_unique(
        where={
            'id': user.id,
        },
        include={  # E: Argument of type "dict[str, dict[str, dict[str, str]]]" cannot be assigned to parameter "include" of type "UserInclude | None" in function "find_unique"
            'posts': {
                'order_by': {
                    'name': 'asc',
                },
            },
        },
    )

    # case: 1-M invalid value
    await client.user.find_unique(
        where={
            'id': user.id,
        },
        include={  # E: Argument of type "dict[str, dict[str, dict[str, str]]]" cannot be assigned to parameter "include" of type "UserInclude | None" in function "find_unique"
            'posts': {
                'order_by': {
                    'published': 'foo',
                },
            },
        },
    )
