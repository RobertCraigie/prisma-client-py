import pytest

from prisma import Prisma, errors
from lib.testing import assert_time_like_now


def test_create(client: Prisma) -> None:
    """Basic record creation"""
    post = client.post.create(
        {
            'title': 'Hi from Prisma!',
            'published': True,
            'description': 'Prisma is a database toolkit that makes databases easy.',
        }
    )
    assert isinstance(post.id, str)
    assert post.title == 'Hi from Prisma!'
    assert post.description == 'Prisma is a database toolkit that makes databases easy.'
    assert post.published is True
    assert_time_like_now(post.created_at)
    assert_time_like_now(post.updated_at)

    user = client.user.create(
        {
            'name': 'Robert',
        }
    )
    assert user.name == 'Robert'
    assert isinstance(user.id, str)


def test_create_with_relationship(client: Prisma) -> None:
    """Creating a record with a nested relationship record creation"""
    post = client.post.create(
        {
            'published': False,
            'title': 'Post 1',
            'author': {'create': {'name': 'Bob'}},
        },
        include={'author': True},
    )
    assert post.author is not None
    assert post.author.name == 'Bob'

    found = client.user.find_unique(where={'id': post.author.id})
    assert found is not None
    assert found.name == 'Bob'


def test_create_missing_required_args(client: Prisma) -> None:
    """Trying to create a record with a missing required field raises an error"""
    with pytest.raises(TypeError):
        client.post.create()  # type: ignore[call-arg]

    with pytest.raises(errors.MissingRequiredValueError):
        client.post.create(
            {  # type: ignore[typeddict-item]
                'published': False,
            }
        )


def test_create_unique_violation(client: Prisma) -> None:
    """Creating the same record twice raises an error"""
    user = client.user.create({'name': 'Robert', 'id': 'user-1'})
    assert user.id == 'user-1'
    assert user.name == 'Robert'

    with pytest.raises(errors.UniqueViolationError):
        client.user.create({'name': 'Robert', 'id': 'user-1'})


def test_setting_field_to_null(client: Prisma) -> None:
    """Creating a field with a None value sets the database record to None"""
    post = client.post.create(
        data={
            'title': 'Post',
            'published': False,
            'description': None,
        },
    )
    assert post.description is None


def test_setting_non_nullable_field_to_null(client: Prisma) -> None:
    """Attempting to create a record with a non-nullable field set to null raises an error"""
    with pytest.raises(errors.MissingRequiredValueError) as exc:
        client.post.create(
            data={
                'title': 'Post',
                'published': None,  # type: ignore
            },
        )

    assert exc.match(r'published')


def test_nullable_relational_field(client: Prisma) -> None:
    """Relational fields cannot be set to None"""
    with pytest.raises(errors.MissingRequiredValueError) as exc:
        client.post.create(
            data={'title': 'Post', 'published': False, 'author': None}  # type: ignore
        )

    assert exc.match(r'author')


def test_required_relation_key_field(client: Prisma) -> None:
    """Explicitly passing a field used as a foreign key connects the relation"""
    user = client.user.create(
        data={
            'name': 'Robert',
        },
    )
    profile = client.profile.create(
        data={
            'description': 'My bio!',
            'country': 'Scotland',
            'user_id': user.id,
        },
        include={
            'user': True,
        },
    )
    assert profile.user is not None
    assert profile.user.id == user.id
    assert profile.user.name == 'Robert'
