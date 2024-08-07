import pytest

from prisma.models import Post, User


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_include_many_order_by() -> None:
    """Including a 1-M relation and ordering it works

    https://github.com/RobertCraigie/prisma-client-py/issues/234
    """
    user = await User.prisma().create(
        data={
            'name': 'Robert',
            'posts': {
                'create': [
                    {
                        'title': 'Post 1',
                        'published': True,
                    },
                    {
                        'title': 'Post 2',
                        'published': False,
                    },
                ]
            },
        },
        include={
            'posts': {
                'order_by': {
                    'title': 'asc',
                },
            },
        },
    )
    assert user.name == 'Robert'
    assert user.posts is not None
    assert len(user.posts) == 2
    assert user.posts[0].title == 'Post 1'
    assert user.posts[1].title == 'Post 2'

    user2 = await User.prisma().find_unique(
        where={
            'id': user.id,
        },
        include={
            'posts': {
                'order_by': {
                    'title': 'desc',
                },
            },
        },
    )
    assert user2 is not None
    assert user2.posts is not None
    assert len(user2.posts) == 2
    assert user2.posts[0].title == 'Post 2'
    assert user2.posts[1].title == 'Post 1'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_connect_or_create() -> None:
    """Connect or create a relation"""
    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
    )

    post = await Post.prisma().create(
        data={
            'title': 'Post 1',
            'published': True,
            'author': {
                'connectOrCreate': {
                    'where': {
                        'id': user.id,
                    },
                    'create': {
                        'name': 'Robert',
                    },
                },
            },
        },
        include={
            'author': True,
        },
    )

    assert post.author is not None
    assert post.author.id == user.id

    post2 = await Post.prisma().create(
        data={
            'title': 'Post 2',
            'published': False,
            'author': {
                'connectOrCreate': {
                    'where': {
                        'id': 'non-existent',
                    },
                    'create': {
                        'name': 'Bobert',
                    },
                },
            },
        },
        include={
            'author': True,
        },
    )

    assert post2.author is not None
    assert post2.author.id != user.id
    assert post2.author.name == 'Bobert'
