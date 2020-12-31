import pytest
from pydantic import ValidationError

from prisma import errors
from .utils import assert_time_like_now


@pytest.mark.asyncio
async def test_create(client):
    post = await client.post.create(
        {
            'title': 'Hi from Prisma!',
            'published': True,
            'desc': 'Prisma is a database toolkit that makes databases easy.',
        }
    )
    assert isinstance(post.id, str)
    assert post.title == 'Hi from Prisma!'
    assert post.desc == 'Prisma is a database toolkit that makes databases easy.'
    assert post.published is True
    assert_time_like_now(post.created_at)
    assert_time_like_now(post.updated_at)

    user = await client.user.create(
        {
            'name': 'Robert',
        }
    )
    assert user.name == 'Robert'
    assert isinstance(user.id, str)


@pytest.mark.asyncio
async def test_create_missing_required_args(client):
    with pytest.raises(ValidationError):
        await client.post.create(
            {
                'title': 'Hi from Prisma!',
            }
        )


@pytest.mark.skip(reason='Data is not cleared between test runs yet')
@pytest.mark.asyncio
async def test_create_unique_violation(client):
    user = await client.user.create({'name': 'Robert', 'id': 'user-1'})
    assert user.name == 'Robert'

    with pytest.raises(errors.UniqueViolationError):
        await client.user.create({'name': 'Robert', 'id': 'user-1'})
