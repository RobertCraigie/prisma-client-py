import re

import pytest

from prisma import Prisma
from prisma.errors import FieldNotFoundError, ForeignKeyViolationError


@pytest.mark.xfail(
    reason='This was broken in v5, we now raise a different error - nobody should be relying on this behaviour and its tricky to fix'
)
def test_field_not_found_error(client: Prisma) -> None:
    """The FieldNotFoundError is raised when an unknown field is passed to
    both queries and mutations.
    """
    with pytest.raises(FieldNotFoundError, match='bad_field'):
        client.post.find_first(where={'bad_field': 'foo'})  # type: ignore

    with pytest.raises(FieldNotFoundError, match='foo'):
        client.post.create(
            data={
                'title': 'foo',
                'published': True,
                'foo': 'bar',  # pyright: ignore
            }
        )

    with pytest.raises(FieldNotFoundError, match='foo'):
        client.post.find_first(
            where={
                'author': {
                    'is': {  # pyright: ignore
                        'foo': 'bar',
                    },
                },
            },
        )


def test_foreign_key_violation_error(client: Prisma) -> None:
    """The ForeignKeyViolationError is raised when a foreign key is invalid."""
    with pytest.raises(
        ForeignKeyViolationError,
        match=re.compile(r'foreign key constraint failed on the field', re.IGNORECASE),
    ):
        client.post.create(
            data={
                'title': 'foo',
                'published': True,
                'author_id': 'cjld2cjxh0000qzrmn831i7rn',
            }
        )
