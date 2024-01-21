import pytest

from prisma.errors import UnknownRelationalFieldError
from prisma.partials import (
    UserOnlyName,
    PostWithAuthor,
    PostOnlyPublished,
    PostWithCustomAuthor,
)


class SubclassedPostOnlyPublished(PostOnlyPublished):
    @property
    def is_public(self) -> bool:
        return self.published


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_scalar_fields() -> None:
    """Querying using a partial model that only has scalar fields"""
    post = await PostOnlyPublished.prisma().create(
        {
            'title': 'foo',
        }
    )
    assert post.published is False
    assert not hasattr(post, 'title')


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_relational_fields() -> None:
    """Querying using a partial model that has relational fields defined"""
    post = await PostWithAuthor.prisma().create(
        {
            'title': 'foo',
            'author': {
                'create': {
                    'name': 'Robert',
                }
            },
        }
    )
    assert post.title == 'foo'
    assert post.author is None

    post2 = await PostWithAuthor.prisma().find_first(
        where={
            'id': post.id,
        },
        include={
            'author': True,
        },
    )
    assert post2 is not None
    assert post2.title == 'foo'
    assert post2.author is not None
    assert post2.author.name == 'Robert'


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_include_missing_relational_field() -> None:
    """Specifying a relational field to include that isn't present on the partial model"""
    user = await UserOnlyName.prisma().create(
        {
            'name': 'Robert',
            'profile': {
                'create': {
                    'description': "Robert's profile",
                    'country': 'Scotland',
                }
            },
        },
    )
    assert user.name == 'Robert'

    with pytest.raises(UnknownRelationalFieldError) as exc:
        await UserOnlyName.prisma().find_first(
            where={'name': 'Robert'},
            include={
                'profile': True,
            },
        )

    assert exc.match(r'Field: "profile" either does not exist or is not a relational field on the UserOnlyName model')


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_custom_relational_fields() -> None:
    """Querying using a partial model that has custom relational fields defined"""
    post = await PostWithCustomAuthor.prisma().create(
        {
            'title': 'foo',
            'author': {
                'create': {
                    'name': 'Robert',
                }
            },
        }
    )
    assert post.title == 'foo'
    assert post.author is None

    post2 = await PostWithCustomAuthor.prisma().find_first(
        where={
            'id': post.id,
        },
        include={
            'author': True,
        },
    )
    assert post2 is not None
    assert post2.title == 'foo'
    assert post2.author is not None
    assert post2.author.name == 'Robert'
    assert isinstance(post2.author, UserOnlyName)


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_custom_model() -> None:
    """Querying using a partial model that has been subclassed"""
    post = await SubclassedPostOnlyPublished.prisma().create(
        {
            'title': 'foo',
            'published': True,
        }
    )
    assert post.is_public
