import pytest

from prisma import Prisma, errors
from prisma.types import UserWhereInput


def test_find_first_or_raise(client: Prisma) -> None:
    """Skips multiple non-matching records"""
    posts = [
        client.post.create(
            {
                'title': 'Test post 1',
                'published': False,
                'views': 100,
            }
        ),
        client.post.create(
            {
                'title': 'Test post 2',
                'published': False,
            }
        ),
        client.post.create(
            {
                'title': 'Test post 3',
                'published': False,
            }
        ),
        client.post.create(
            {
                'title': 'Test post 4',
                'published': True,
                'views': 500,
            }
        ),
        client.post.create(
            {
                'title': 'Test post 5',
                'published': False,
            }
        ),
        client.post.create(
            {
                'title': 'Test post 6',
                'published': True,
            }
        ),
    ]

    post = client.post.find_first_or_raise(
        where={
            'published': True,
        },
        order={
            'title': 'asc',
        },
    )
    assert post.id == posts[3].id
    assert post.title == 'Test post 4'
    assert post.published is True

    with pytest.raises(
        errors.RecordNotFoundError,
        match=r'depends on one or more records that were required but not found',
    ):
        client.post.find_first_or_raise(
            where={
                'title': {
                    'contains': 'not found',
                }
            }
        )

    post = client.post.find_first_or_raise(
        where={
            'published': True,
        },
        order={
            'title': 'asc',
        },
        skip=1,
    )
    assert post.id == posts[5].id
    assert post.title == 'Test post 6'
    assert post.published is True

    post = client.post.find_first_or_raise(
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
    assert post.title == 'Test post 1'

    post = client.post.find_first_or_raise(
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
    assert post.title == 'Test post 3'

    post = client.post.find_first_or_raise(
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
        order={
            'created_at': 'asc',
        },
    )
    assert post.title == 'Test post 4'

    post = client.post.find_first_or_raise(
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
        order={
            'created_at': 'asc',
        },
    )
    assert post.title == 'Test post 4'

    with pytest.raises(errors.RecordNotFoundError):
        client.post.find_first_or_raise(
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

    post = client.post.find_first_or_raise(
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
        },
        order={
            'created_at': 'asc',
        },
    )
    assert post.title == 'Test post 1'

    post = client.post.find_first_or_raise(
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
    assert post.title == 'Test post 4'


def test_filtering_one_to_one_relation(client: Prisma) -> None:
    """Filtering by a 1-1 relational field and negating the filter"""
    with client.batch_() as batcher:
        batcher.user.create(
            {
                'name': 'Robert',
                'profile': {
                    'create': {
                        'description': 'My very cool bio.',
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
                        'description': 'Hello world, this is my bio.',
                        'country': 'Scotland',
                    },
                },
            },
        )
        batcher.user.create({'name': 'Callum'})

    user = client.user.find_first_or_raise(
        where={
            'profile': {
                'is': {
                    'description': {
                        'contains': 'cool',
                    }
                }
            }
        }
    )
    assert user.name == 'Robert'
    assert user.profile is None

    user = client.user.find_first_or_raise(
        where={
            'profile': {
                'is_not': {
                    'description': {
                        'contains': 'bio',
                    }
                }
            }
        }
    )
    assert user.name == 'Callum'
    assert user.profile is None


def test_filtering_and_ordering_one_to_many_relation(
    client: Prisma,
) -> None:
    """Filtering with every, some, none and ordering by a 1-M relational field"""
    with client.batch_() as batcher:
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

    user = client.user.find_first_or_raise(
        where={
            'posts': {
                'every': {
                    'title': {
                        'contains': 'post',
                    }
                }
            }
        },
    )
    assert user.name == 'Robert'

    user = client.user.find_first_or_raise(
        where={
            'posts': {
                'none': {
                    'title': {
                        'contains': 'Post',
                    }
                }
            }
        },
        order={
            'name': 'asc',
        },
    )
    assert user.name == 'Callum'

    with pytest.raises(errors.RecordNotFoundError):
        client.user.find_first_or_raise(
            where={
                'posts': {
                    'some': {
                        'title': 'foo',
                    }
                }
            }
        )

    # ordering

    user = client.user.find_first_or_raise(
        where={
            'posts': {
                'some': {
                    'title': {
                        'contains': 'post',
                    }
                }
            }
        },
        order={'name': 'asc'},
    )
    assert user.name == 'Robert'

    user = client.user.find_first_or_raise(
        where={
            'posts': {
                'some': {
                    'title': {
                        'contains': 'post',
                    }
                }
            }
        },
        order={'name': 'desc'},
    )
    assert user.name == 'Tegan'


def test_list_wrapper_query_transformation(client: Prisma) -> None:
    """Queries wrapped within a list transform global aliases"""
    query: UserWhereInput = {
        'OR': [
            {'name': {'startswith': '40'}},
            {'name': {'contains': ', 40'}},
            {'name': {'contains': 'house'}},
        ]
    }

    client.user.create({'name': 'Robert house'})
    found = client.user.find_first_or_raise(where=query, order={'created_at': 'asc'})
    assert found.name == 'Robert house'

    client.user.create({'name': '40 robert'})
    found = client.user.find_first_or_raise(skip=1, where=query, order={'created_at': 'asc'})
    assert found.name == '40 robert'


def test_distinct(client: Prisma) -> None:
    """Filtering by distinct combinations of fields"""
    users = [
        client.user.create(
            data={
                'name': 'Robert',
            },
        ),
        client.user.create(
            data={
                'name': 'Tegan',
            },
        ),
        client.user.create(
            data={
                'name': 'Patrick',
            },
        ),
    ]
    with client.batch_() as batcher:
        batcher.profile.create(
            {
                'city': 'Dundee',
                'country': 'Scotland',
                'description': 'Foo',
                'user_id': users[0].id,
            }
        )
        batcher.profile.create(
            {
                'city': 'Edinburgh',
                'country': 'Scotland',
                'description': 'Foo',
                'user_id': users[1].id,
            }
        )
        batcher.profile.create(
            {
                'city': 'London',
                'country': 'England',
                'description': 'Foo',
                'user_id': users[2].id,
            }
        )

    found = client.profile.find_first_or_raise(
        where={'country': 'Scotland'},
        distinct=['city'],
        order={'city': 'asc'},
    )
    assert found.city == 'Dundee'

    found = client.profile.find_first_or_raise(
        where={'country': 'Scotland'},
        distinct=['city'],
        order={'city': 'desc'},
    )
    assert found.city == 'Edinburgh'


def test_distinct_relations(client: Prisma) -> None:
    """Using `distinct` across relations"""
    user = client.user.create(
        {
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
                    {
                        'title': 'Post 3',
                        'published': True,
                    },
                ]
            },
        }
    )

    found = client.user.find_first_or_raise(
        where={
            'id': user.id,
        },
        include={
            'posts': {
                'order_by': {'title': 'asc'},
                'distinct': ['published'],
            }
        },
    )
    assert found.posts is not None
    assert len(found.posts) == 2
    assert found.posts[0].published is True
    assert found.posts[1].published is False
