import pytest
from prisma import Prisma
from prisma.types import UserWhereInput


@pytest.mark.asyncio
async def test_find_first(client: Prisma) -> None:
    """Skips multiple non-matching records"""
    posts = [
        await client.post.create(
            {
                'title': 'Test post 1',
                'published': False,
                'views': 100,
            }
        ),
        await client.post.create(
            {
                'title': 'Test post 2',
                'published': False,
            }
        ),
        await client.post.create(
            {
                'title': 'Test post 3',
                'published': False,
            }
        ),
        await client.post.create(
            {
                'title': 'Test post 4',
                'published': True,
                'views': 500,
            }
        ),
        await client.post.create(
            {
                'title': 'Test post 5',
                'published': False,
            }
        ),
        await client.post.create(
            {
                'title': 'Test post 6',
                'published': True,
            }
        ),
    ]

    post = await client.post.find_first(where={'published': True})
    assert post is not None
    assert post.id == posts[3].id
    assert post.title == 'Test post 4'
    assert post.published is True

    post = await client.post.find_first(
        where={'title': {'contains': 'not found'}}
    )
    assert post is None

    post = await client.post.find_first(where={'published': True}, skip=1)
    assert post is not None
    assert post.id == posts[5].id
    assert post.title == 'Test post 6'
    assert post.published is True

    post = await client.post.find_first(
        where={
            'NOT': [
                {
                    'published': True,
                },
            ],
        },
        order={
            'created_at': 'asc',
        },
    )
    assert post is not None
    assert post.title == 'Test post 1'

    post = await client.post.find_first(
        where={
            'NOT': [
                {
                    'title': {
                        'contains': '1',
                    },
                },
                {
                    'title': {
                        'contains': '2',
                    },
                },
            ],
        },
        order={
            'created_at': 'asc',
        },
    )
    assert post is not None
    assert post.title == 'Test post 3'

    post = await client.post.find_first(
        where={
            'title': {
                'contains': 'Test',
            },
            'AND': [
                {
                    'published': True,
                },
            ],
        },
    )
    assert post is not None
    assert post.title == 'Test post 4'

    post = await client.post.find_first(
        where={
            'AND': [
                {
                    'published': True,
                },
                {
                    'title': {
                        'contains': 'Test',
                    }
                },
            ],
        },
    )
    assert post is not None
    assert post.title == 'Test post 4'

    post = await client.post.find_first(
        where={
            'views': {
                'gt': 100,
            },
            'OR': [
                {
                    'published': False,
                },
            ],
        }
    )
    assert post is None

    post = await client.post.find_first(
        where={
            'OR': [
                {
                    'views': {
                        'gt': 100,
                    },
                },
                {
                    'published': False,
                },
            ]
        }
    )
    assert post is not None
    assert post.title == 'Test post 1'

    post = await client.post.find_first(
        where={
            'OR': [
                {
                    'views': {
                        'gt': 100,
                    },
                },
            ]
        }
    )
    assert post is not None
    assert post.title == 'Test post 4'


@pytest.mark.asyncio
async def test_filtering_one_to_one_relation(client: Prisma) -> None:
    """Filtering by a 1-1 relational field and negating the filter"""
    async with client.batch_() as batcher:
        batcher.user.create(
            {
                'name': 'Robert',
                'profile': {
                    'create': {
                        'bio': 'My very cool bio.',
                        'country': 'Scotland',
                    },
                },
            },
        )
        batcher.user.create(
            {
                'name': 'Tegan',
                'profile': {
                    'create': {
                        'bio': 'Hello world, this is my bio.',
                        'country': 'Scotland',
                    },
                },
            },
        )
        batcher.user.create({'name': 'Callum'})

    user = await client.user.find_first(
        where={'profile': {'is': {'bio': {'contains': 'cool'}}}}
    )
    assert user is not None
    assert user.name == 'Robert'
    assert user.profile is None

    user = await client.user.find_first(
        where={'profile': {'is_not': {'bio': {'contains': 'bio'}}}}
    )
    assert user is not None
    assert user.name == 'Callum'
    assert user.profile is None


@pytest.mark.asyncio
async def test_filtering_and_ordering_one_to_many_relation(
    client: Prisma,
) -> None:
    """Filtering with every, some, none and ordering by a 1-M relational field"""
    async with client.batch_() as batcher:
        batcher.user.create(
            {
                'name': 'Robert',
                'posts': {
                    'create': [
                        {'title': 'My first post', 'published': True},
                        {'title': 'My second post', 'published': False},
                    ]
                },
            }
        )
        batcher.user.create(
            {
                'name': 'Tegan',
                'posts': {
                    'create': [
                        {'title': 'Hello, world!', 'published': True},
                        {'title': 'My test post', 'published': False},
                    ]
                },
            }
        )
        batcher.user.create({'name': 'Callum'})

    user = await client.user.find_first(
        where={'posts': {'every': {'title': {'contains': 'post'}}}},
    )
    assert user is not None
    assert user.name == 'Robert'

    user = await client.user.find_first(
        where={'posts': {'none': {'title': {'contains': 'Post'}}}}
    )
    assert user is not None
    assert user.name == 'Callum'

    user = await client.user.find_first(
        where={'posts': {'some': {'title': 'foo'}}}
    )
    assert user is None

    # ordering

    user = await client.user.find_first(
        where={'posts': {'some': {'title': {'contains': 'post'}}}},
        order={'name': 'asc'},
    )
    assert user is not None
    assert user.name == 'Robert'

    user = await client.user.find_first(
        where={'posts': {'some': {'title': {'contains': 'post'}}}},
        order={'name': 'desc'},
    )
    assert user is not None
    assert user.name == 'Tegan'


@pytest.mark.asyncio
async def test_list_wrapper_query_transformation(client: Prisma) -> None:
    """Queries wrapped within a list transform global aliases"""
    query: UserWhereInput = {
        'OR': [
            {'name': {'startswith': '40'}},
            {'name': {'contains': ', 40'}},
            {'name': {'contains': 'house'}},
        ]
    }

    await client.user.create({'name': 'Robert house'})
    found = await client.user.find_first(
        where=query, order={'created_at': 'asc'}
    )
    assert found is not None
    assert found.name == 'Robert house'

    await client.user.create({'name': '40 robert'})
    found = await client.user.find_first(
        skip=1, where=query, order={'created_at': 'asc'}
    )
    assert found is not None
    assert found.name == '40 robert'
