from prisma import Prisma


async def test_find_unique_include(client: Prisma, user_id: str) -> None:
    user = await client.user.find_unique(
        where={
            'id': user_id,
        },
        include={
            'posts': True,
        },
    )
    assert user is not None
    assert user.name == 'Robert'

    # the mypy plugin should be able to change the `user.posts` type from
    # `List[Post] | None` -> `List[Post]` because of the `include` argument above
    assert len(user.posts) == 4

    for i, post in enumerate(user.posts, start=1):
        assert post.author is None
        assert post.author_id == user.id
        assert post.title == f'Post {i}'
