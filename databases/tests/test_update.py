import pytest

import prisma
from prisma import Prisma
from lib.testing import async_fixture
from prisma.models import User, Types, Unique2

from ..utils import CURRENT_DATABASE


@async_fixture(name='user_id')
async def user_id_fixture(client: Prisma) -> str:
    user = await client.user.create({'name': 'Robert'})
    return user.id


@pytest.mark.asyncio
async def test_update(client: Prisma) -> None:
    """Standard usage"""
    post = await client.post.create(
        {
            'title': 'Hi from Create!',
            'published': True,
            'description': 'Prisma is a database toolkit that makes databases easy.',
            'author': {
                'create': {
                    'name': 'Bob',
                },
            },
        }
    )
    assert post.author is None
    assert post.title == 'Hi from Create!'
    updated = await client.post.update(
        where={
            'id': post.id,
        },
        data={
            'title': 'Hi from Update!',
        },
    )
    assert updated is not None
    assert updated.title == 'Hi from Update!'
    assert updated.updated_at != post.updated_at
    assert updated.created_at == post.created_at

    updated = await client.post.update(
        where={
            'id': post.id,
        },
        include={
            'author': True,
        },
        data={
            'published': False,
            'description': 'Updated desc.',
        },
    )
    assert updated is not None
    assert updated.published is False
    assert updated.description == 'Updated desc.'
    assert updated.author is not None
    assert updated.author.name == 'Bob'


@pytest.mark.asyncio
@pytest.mark.parametrize('method', ['disconnect', 'delete'])
async def test_update_with_create_disconnect(client: Prisma, user_id: str, method: str) -> None:
    """Removing a relational field"""
    user = await client.user.find_unique(where={'id': user_id}, include={'posts': True})
    assert user is not None
    assert user.posts is not None
    assert len(user.posts) == 0

    updated = await client.user.update(
        where={'id': user_id},
        data={'posts': {'create': [{'title': 'My post', 'published': True}]}},
        include={'posts': True},
    )
    assert updated is not None
    assert updated.posts is not None
    assert len(updated.posts) == 1

    post_id = updated.posts[0].id

    if method == 'disconnect':
        updated = await client.user.update(
            where={'id': user_id},
            data={
                'posts': {
                    'disconnect': [
                        {'id': post_id},
                    ]
                }
            },
            include={'posts': True},
        )
    else:
        updated = await client.user.update(
            where={'id': user_id},
            data={
                'posts': {
                    'delete': [
                        {'id': post_id},
                    ],
                }
            },
            include={'posts': True},
        )

    assert updated is not None
    assert updated.posts is not None
    assert len(updated.posts) == 0


@pytest.mark.asyncio
async def test_atomic_update(client: Prisma) -> None:
    """Atomically incrementing a value by 1"""
    post = await client.post.create({'title': 'My Post', 'published': False})
    assert post.title == 'My Post'
    assert post.views == 0

    updated = await client.post.update(where={'id': post.id}, data={'views': {'increment': 1}})
    assert updated is not None
    assert updated.views == 1


@pytest.mark.asyncio
async def test_update_record_not_found(client: Prisma) -> None:
    """Updating a non-existent record returns None"""
    post = await client.post.update(where={'id': 'wow'}, data={'title': 'Hi from Update!'})
    assert post is None


@pytest.mark.asyncio
async def test_setting_field_to_null(client: Prisma) -> None:
    """Updating a field to None sets the database record to None"""
    post = await client.post.create(
        data={
            'title': 'Post',
            'published': False,
            'description': 'My description',
        },
    )
    assert post.description == 'My description'

    updated = await client.post.update(
        where={
            'id': post.id,
        },
        data={'description': None},
    )
    assert updated is not None
    assert updated.id == post.id
    assert updated.description is None


@pytest.mark.asyncio
async def test_setting_non_nullable_field_to_null(client: Prisma) -> None:
    """Attempting to set a non-nullable field to null raises an error"""
    post = await client.post.create(
        data={
            'title': 'Post',
            'published': False,
        },
    )
    assert post.published is False

    with pytest.raises(prisma.errors.MissingRequiredValueError) as exc:
        await client.post.update(
            where={
                'id': post.id,
            },
            data={'published': None},  # type: ignore
        )

    assert exc.match(r'published')


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_update_id_field() -> None:
    """Setting an ID field"""
    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
    )
    updated = await User.prisma().update(
        where={
            'id': user.id,
        },
        data={
            'id': 'abcd123',
        },
    )
    assert updated is not None
    assert updated.id == 'abcd123'


@pytest.mark.prisma
@pytest.mark.asyncio
@pytest.mark.skipif(
    CURRENT_DATABASE == 'cockroachdb',
    reason='https://github.com/prisma/prisma/issues/16612',
)
async def test_update_id_field_atomic() -> None:
    """Setting an ID field atomically"""
    record = await Types.prisma().create({})
    updated = await Types.prisma().update(
        where={
            'id': record.id,
        },
        data={
            'id': {
                'increment': 500,
            },
        },
    )
    assert updated is not None
    assert updated.id == record.id + 500


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_update_unique_field() -> None:
    """Setting a unique field"""
    record = await Unique2.prisma().create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        }
    )

    updated = await Unique2.prisma().update(
        where={
            'surname': record.surname,
        },
        data={
            'surname': 'George',
        },
    )
    assert updated is not None
    assert updated.name == record.name
    assert updated.surname == 'George'
