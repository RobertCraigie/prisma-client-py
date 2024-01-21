import re

import pytest

import prisma
from prisma import Prisma
from prisma.errors import FieldNotFoundError, ForeignKeyViolationError


@pytest.mark.xfail(
    reason='This was broken in v5, we now raise a different error - nobody should be relying on this behaviour and its tricky to fix'
)
@pytest.mark.asyncio
async def test_field_not_found_error(client: Prisma) -> None:
    """The FieldNotFoundError is raised when an unknown field is passed to
    both queries and mutations.
    """
    with pytest.raises(FieldNotFoundError, match='bad_field'):
        await client.post.find_first(where={'bad_field': 'foo'})  # type: ignore

    with pytest.raises(FieldNotFoundError, match='data.foo'):
        await client.post.create(
            data={
                'title': 'foo',
                'published': True,
                'foo': 'bar',  # pyright: ignore
            }
        )

    with pytest.raises(FieldNotFoundError, match='where.author.is.foo'):
        await client.post.find_first(
            where={
                'author': {
                    'is': {  # pyright: ignore
                        'foo': 'bar',
                    },
                },
            },
        )


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_field_not_found_error_selection() -> None:
    """The FieldNotFoundError is raised when an unknown field is passed to selections."""

    class CustomPost(prisma.bases.BasePost):
        foo_field: str

    with pytest.raises(
        FieldNotFoundError,
        match=r'Field \'foo_field\' not found in enclosing type \'Post\'',
    ):
        await CustomPost.prisma().find_first()


@pytest.mark.asyncio
async def test_foreign_key_violation_error(client: Prisma) -> None:
    """The ForeignKeyViolationError is raised when a foreign key is invalid."""
    with pytest.raises(
        ForeignKeyViolationError,
        match=re.compile(r'foreign key constraint failed on the field', re.IGNORECASE),
    ):
        await client.post.create(
            data={
                'title': 'foo',
                'published': True,
                'author_id': 'cjld2cjxh0000qzrmn831i7rn',
            }
        )
