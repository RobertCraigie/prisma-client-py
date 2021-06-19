import pytest

from prisma import errors, Client
from .utils import assert_time_like_now


@pytest.mark.asyncio
async def test_create(client: Client) -> None:
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
async def test_create_with_relationship(client: Client) -> None:
    post = await client.post.create(
        {
            'published': False,
            'title': 'Post 1',
            'author': {'create': {'name': 'Bob'}},
        },
        include={'author': True},
    )
    assert post.author is not None
    assert post.author.name == 'Bob'

    found = await client.user.find_unique(where={'id': post.author.id})
    assert found is not None
    assert found.name == 'Bob'


@pytest.mark.asyncio
async def test_create_missing_required_args(client: Client) -> None:
    with pytest.raises(TypeError):
        await client.post.create()  # type: ignore[call-arg]

    with pytest.raises(errors.MissingRequiredValueError):
        await client.post.create(
            {  # type: ignore[typeddict-item]
                'title': 'Hi from Prisma!',
            }
        )


@pytest.mark.asyncio
async def test_create_unique_violation(client: Client) -> None:
    user = await client.user.create({'name': 'Robert', 'id': 'user-1'})
    assert user.id == 'user-1'
    assert user.name == 'Robert'

    with pytest.raises(errors.UniqueViolationError):
        await client.user.create({'name': 'Robert', 'id': 'user-1'})
