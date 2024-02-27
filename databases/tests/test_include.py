from typing import List

import pytest

from prisma import Prisma
from lib.testing import async_fixture
from prisma.models import Post


@async_fixture(scope='module', name='user_id')
async def user_id_fixture(client: Prisma) -> str:
    user = await client.user.create({'name': 'Robert'})
    posts = await create_or_get_posts(client, user.id)
    await client.custom_category.create(
        {
            'name': 'My Category',
            'posts': {'connect': [{'id': posts[0].id}, {'id': posts[1].id}]},
        }
    )
    return user.id


@async_fixture(scope='module', name='posts')
async def posts_fixture(client: Prisma, user_id: str) -> List[Post]:
    return await create_or_get_posts(client, user_id)


async def create_or_get_posts(client: Prisma, user_id: str) -> List[Post]:
    user = await client.user.find_unique(
        where={'id': user_id},
        include={
            'posts': {
                'order_by': {
                    'title': 'asc',
                },
            },
        },
    )
    assert user is not None

    if user.posts:
        return user.posts

    return [
        await client.post.create(
            {
                'title': 'Post 1',
                'published': False,
                'author': {'connect': {'id': user_id}},
            }
        ),
        await client.post.create(
            {
                'title': 'Post 2',
                'published': True,
                'author': {'connect': {'id': user_id}},
            }
        ),
        await client.post.create(
            {
                'title': 'Post 3',
                'published': True,
                'author': {'connect': {'id': user_id}},
            }
        ),
        await client.post.create(
            {
                'title': 'Post 4',
                'published': False,
                'author': {'connect': {'id': user_id}},
            }
        ),
    ]


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_find_unique_include(client: Prisma, user_id: str) -> None:
    """Including a one-to-many relationship returns all records as a list of models"""
    user = await client.user.find_unique(
        where={'id': user_id},
        include={
            'posts': {
                'order_by': {'title': 'asc'},
            }
        },
    )
    assert user is not None
    assert user.name == 'Robert'
    assert user.posts is not None
    assert len(user.posts) == 4

    for i, post in enumerate(
        user.posts,
        start=1,
    ):
        assert post.author is None
        assert post.author_id == user.id
        assert post.title == f'Post {i}'


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_find_unique_include_take(client: Prisma, user_id: str) -> None:
    """Including a one-to-many relationship with take limits amount of returned models"""
    user = await client.user.find_unique(
        where={
            'id': user_id,
        },
        include={
            'posts': {
                'take': 1,
            },
        },
    )
    assert user is not None
    assert user.posts is not None
    assert len(user.posts) == 1


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_find_unique_include_where(client: Prisma, user_id: str, posts: List[Post]) -> None:
    """Including a one-to-many relationship with a where argument filters results"""
    user = await client.user.find_unique(
        where={'id': user_id},
        include={'posts': {'where': {'created_at': posts[0].created_at}}},
    )
    assert user is not None
    assert user.posts is not None
    assert len(user.posts) == 1
    assert user.posts[0].id == posts[0].id


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_find_unique_include_pagination(client: Prisma, user_id: str, posts: List[Post]) -> None:
    """Pagination by cursor id works forwards and backwards"""
    user = await client.user.find_unique(
        where={'id': user_id},
        include={
            'posts': {
                'cursor': {'id': posts[0].id},
                'take': 1,
                'skip': 1,
                'order_by': {
                    'title': 'asc',
                },
            }
        },
    )
    assert user is not None
    assert user.posts is not None
    assert len(user.posts) == 1
    assert user.posts[0].id == posts[1].id

    user = await client.user.find_unique(
        where={'id': user_id},
        include={
            'posts': {
                'cursor': {'id': posts[1].id},
                'take': -1,
                'skip': 1,
                'order_by': {
                    'title': 'asc',
                },
            },
        },
    )
    assert user is not None
    assert user.posts is not None
    assert len(user.posts) == 1
    assert user.posts[0].id == posts[0].id


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_find_unique_include_nested_where_or(client: Prisma, user_id: str, posts: List[Post]) -> None:
    """Include with nested or argument"""
    user = await client.user.find_unique(
        where={'id': user_id},
        include={
            'posts': {
                'where': {
                    'OR': [
                        {'id': posts[0].id},
                        {'published': True},
                    ],
                },
                'order_by': {
                    'title': 'asc',
                },
            }
        },
    )
    assert user is not None

    assert posts[0].published is False
    assert user.posts is not None
    assert len(user.posts) == 3

    assert user.posts[0].id == posts[0].id
    assert user.posts[1].id == posts[1].id
    assert user.posts[2].id == posts[2].id

    assert user.posts[0].published is False
    assert user.posts[1].published is True
    assert user.posts[2].published is True


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_find_unique_include_nested_include(client: Prisma, user_id: str) -> None:
    """Multiple nested include arguments returns all models"""
    user = await client.user.find_unique(
        where={'id': user_id},
        include={
            'profile': True,
            'posts': {'include': {'categories': {'include': {'posts': True}}}},
        },
    )
    assert user is not None
    assert user.profile is None
    assert user.posts is not None
    for post in user.posts:
        assert post.categories is not None
        for category in post.categories:
            assert category.posts is not None


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_create_include(client: Prisma) -> None:
    """Creating a record and including it at the same time"""
    post = await client.post.create(
        {
            'title': 'Post 4',
            'published': False,
            'author': {'create': {'name': 'Bob'}},
        },
        include={'author': True},
    )
    assert post.author is not None
    assert post.author.name == 'Bob'
