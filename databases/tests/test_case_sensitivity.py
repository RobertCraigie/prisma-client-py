import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_case_sensitivity(client: Prisma) -> None:
    """Ensure string fields can be filtered in a case-insensitive manner"""
    await client.user.create(
        data={
            'name': 'Robert',
            'posts': {
                'create': {
                    'title': 'POST 1',
                },
            },
        },
    )
    await client.user.create(
        data={
            'name': 'robert',
            'posts': {
                'create': {
                    'title': 'post 2',
                },
            },
        },
    )

    users = await client.user.find_many(
        where={
            'name': {
                'equals': 'robert',
                'mode': 'insensitive',
            },
        },
        order={
            'created_at': 'asc',
        },
    )
    assert len(users) == 2
    assert users[0].name == 'Robert'
    assert users[1].name == 'robert'

    users = await client.user.find_many(
        where={
            'name': {
                'equals': 'robert',
                'mode': 'default',
            },
        },
    )
    assert len(users) == 1
    assert users[0].name == 'robert'

    users = await client.user.find_many(
        where={
            'name': {
                'equals': 'robert',
            },
        },
    )
    assert len(users) == 1
    assert users[0].name == 'robert'

    posts = await client.post.find_many(
        where={
            'author': {
                'is': {
                    'name': {
                        'equals': 'robert',
                        'mode': 'insensitive',
                    },
                },
            },
        },
        include={
            'author': True,
        },
        order={
            'created_at': 'asc',
        },
    )
    assert len(posts) == 2
    assert posts[0].title == 'POST 1'
    assert posts[0].author is not None
    assert posts[0].author.name == 'Robert'
    assert posts[1].title == 'post 2'
    assert posts[1].author is not None
    assert posts[1].author.name == 'robert'
