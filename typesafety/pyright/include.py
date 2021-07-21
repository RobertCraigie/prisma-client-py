from prisma import Client


async def main(client: Client) -> None:
    user = await client.user.find_unique(where={'id': '1'}, include={'posts': True})
    reveal_type(user)  # T: User | None
    assert user is not None

    for post in user.posts:  # E: Object of type "None" cannot be used as iterable value
        ...

    assert user.posts is not None
    for post in user.posts:
        ...

    reveal_type(user.posts)  # T: List[Post]
