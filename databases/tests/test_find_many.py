import pytest

import prisma
from prisma import Prisma


@pytest.mark.asyncio
async def test_find_many(client: Prisma) -> None:
    """Filters and ordering work as suggested"""
    posts = [
        await client.post.create({'title': 'Test post 1', 'published': False}),
        await client.post.create({'title': 'Test post 2', 'published': False}),
    ]
    found = await client.post.find_many(where={'title': 'Test post 1'})
    assert len(found) == 1
    assert found[0].id == posts[0].id

    posts = await client.post.find_many(where={'OR': [{'title': 'Test post 1'}, {'title': 'Test post 2'}]})
    assert len(posts) == 2

    posts = await client.post.find_many(where={'title': {'contains': 'Test post'}})
    assert len(posts) == 2

    posts = await client.post.find_many(where={'title': {'startswith': 'Test post'}})
    assert len(posts) == 2

    posts = await client.post.find_many(where={'title': {'not_in': ['Test post 1']}})
    assert len(posts) == 1
    assert posts[0].title == 'Test post 2'

    posts = await client.post.find_many(where={'title': {'equals': 'Test post 2'}})
    assert len(posts) == 1
    assert posts[0].title == 'Test post 2'

    posts = await client.post.find_many(where={'title': 'Test post 2'})
    assert len(posts) == 1
    assert posts[0].title == 'Test post 2'

    posts = await client.post.find_many(order={'title': 'desc'})
    assert len(posts) == 2
    assert posts[0].title == 'Test post 2'
    assert posts[1].title == 'Test post 1'

    posts = await client.post.find_many(order={'title': 'asc'})
    assert len(posts) == 2
    assert posts[0].title == 'Test post 1'
    assert posts[1].title == 'Test post 2'


@pytest.mark.asyncio
async def test_cursor(client: Prisma) -> None:
    """Cursor argument correctly paginates results"""
    posts = [
        await client.post.create({'title': 'Foo 1', 'published': False}),
        await client.post.create({'title': 'Foo 2', 'published': False}),
        await client.post.create({'title': 'Foo 3', 'published': False}),
        await client.post.create({'title': 'Foo 4', 'published': False}),
    ]
    found = await client.post.find_many(
        cursor={
            'id': posts[1].id,
        },
        order={
            'title': 'asc',
        },
    )
    assert len(found) == 3
    assert found[0].title == 'Foo 2'
    assert found[1].title == 'Foo 3'
    assert found[2].title == 'Foo 4'

    found = await client.post.find_many(
        cursor={
            'id': posts[3].id,
        },
        order={
            'title': 'asc',
        },
    )
    assert len(found) == 1
    assert found[0].title == 'Foo 4'


@pytest.mark.asyncio
async def test_filtering_one_to_one_relation(client: Prisma) -> None:
    """Filtering by a 1-1 relational field and negating the filter"""
    async with client.batch_() as batcher:
        batcher.user.create(
            {
                'name': 'Robert',
                'profile': {
                    'create': {
                        'description': 'My very cool bio.',
                        'country': 'Scotland',
                    }
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

    users = await client.user.find_many(
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
    assert len(users) == 1
    assert users[0].name == 'Robert'
    assert users[0].profile is None

    users = await client.user.find_many(
        where={
            'profile': {
                'is': {
                    'description': {
                        'contains': 'bio',
                    },
                },
            },
        },
        order={
            'name': 'asc',
        },
    )
    assert len(users) == 2
    assert users[0].name == 'Robert'
    assert users[1].name == 'Tegan'

    users = await client.user.find_many(
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
    assert len(users) == 1
    assert users[0].name == 'Callum'


@pytest.mark.asyncio
async def test_filtering_one_to_many_relation(client: Prisma) -> None:
    """Filtering by a 1-M relational field and negating the filter"""
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

    # I guess it makes sense that a record with no relations also matches this
    # TODO: this needs to be documented
    users = await client.user.find_many(
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
    assert len(users) == 2
    assert users[0].name == 'Robert'
    assert users[1].name == 'Callum'

    users = await client.user.find_many(
        where={
            'posts': {
                'some': {
                    'title': {
                        'contains': 'post',
                    }
                }
            }
        },
        order={
            'name': 'asc',
        },
    )
    assert len(users) == 2
    assert users[0].name == 'Robert'
    assert users[1].name == 'Tegan'

    users = await client.user.find_many(
        where={
            'posts': {
                'none': {
                    'title': {
                        'contains': 'post',
                    }
                }
            }
        }
    )
    assert len(users) == 1
    assert users[0].name == 'Callum'

    users = await client.user.find_many(
        where={
            'posts': {
                'some': {
                    'title': 'foo',
                }
            }
        }
    )
    assert len(users) == 0


@pytest.mark.asyncio
async def test_ordering(client: Prisma) -> None:
    """Ordering by `asc` and `desc` correctly changes the order of the returned records"""
    async with client.batch_() as batcher:
        batcher.post.create({'title': 'Test post 1', 'published': False})
        batcher.post.create({'title': 'Test post 2', 'published': False})
        batcher.post.create({'title': 'Test post 3', 'published': True})

    found = await client.post.find_many(
        where={'title': {'contains': 'Test'}},
        order={'published': 'asc'},
    )
    assert len(found) == 3
    assert found[0].published is False
    assert found[1].published is False
    assert found[2].published is True

    found = await client.post.find_many(
        where={'title': {'contains': 'Test'}},
        order={'published': 'desc'},
    )
    assert len(found) == 3
    assert found[0].published is True
    assert found[1].published is False
    assert found[2].published is False

    # multiple fields in the same `order` dictionary are not supported
    with pytest.raises(prisma.errors.DataError):
        await client.post.find_many(
            where={
                'title': {
                    'contains': 'Test',
                },
            },
            order={  # type: ignore
                'published': 'desc',
                'title': 'desc',
            },
        )


@pytest.mark.asyncio
@pytest.mark.skip(reason='incorrect error is raised here - requires an overhaul of the error system')
async def test_too_many_fields_error(client: Prisma) -> None:
    """Passing in multiple fields in order is not supported"""
    with pytest.raises(prisma.errors.DataError) as exc:
        await client.post.find_many(
            where={
                'title': {
                    'contains': 'Test',
                },
            },
            order={  # type: ignore
                'published': 'desc',
                'title': 'desc',
            },
        )

    assert exc.match(r'Expected a minimum of 0 and at most 1 fields to be present, got 2')


@pytest.mark.asyncio
async def test_order_field_not_nullable(client: Prisma) -> None:
    """Order by fields, if present, cannot be None"""
    with pytest.raises(prisma.errors.FieldNotFoundError, match=r'orderBy.desc'):
        await client.post.find_many(order={'desc': None})  # type: ignore


@pytest.mark.asyncio
async def test_distinct(client: Prisma) -> None:
    """Filtering by distinct combinations of fields"""
    users = [
        await client.user.create(
            data={
                'name': 'Robert',
            },
        ),
        await client.user.create(
            data={
                'name': 'Tegan',
            },
        ),
        await client.user.create(
            data={
                'name': 'Patrick',
            },
        ),
    ]
    async with client.batch_() as batcher:
        batcher.profile.create(
            {
                'city': 'Paris',
                'country': 'France',
                'description': 'Foo',
                'user_id': users[0].id,
            }
        )
        batcher.profile.create(
            {
                'city': 'Lyon',
                'country': 'France',
                'description': 'Foo',
                'user_id': users[1].id,
            }
        )
        batcher.profile.create(
            {
                'city': 'Paris',
                'country': 'Denmark',
                'description': 'Foo',
                'user_id': users[2].id,
            }
        )

    results = await client.profile.find_many(
        distinct=['country'],
        order={
            'country': 'asc',
        },
    )
    assert len(results) == 2
    assert results[0].country == 'Denmark'
    assert results[1].country == 'France'

    results = await client.profile.find_many(
        distinct=['city'],
        order={
            'city': 'asc',
        },
    )
    assert len(results) == 2
    assert results[0].city == 'Lyon'
    assert results[1].city == 'Paris'

    results = await client.profile.find_many(
        distinct=['city', 'country'],
        order=[
            {
                'city': 'asc',
            },
            {
                'country': 'asc',
            },
        ],
    )
    assert len(results) == 3
    assert results[0].city == 'Lyon'
    assert results[0].country == 'France'
    assert results[1].city == 'Paris'
    assert results[1].country == 'Denmark'
    assert results[2].city == 'Paris'
    assert results[2].country == 'France'
