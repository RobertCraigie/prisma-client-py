import pytest

from prisma import Prisma
from prisma.errors import FieldNotFoundError


@pytest.mark.asyncio
async def test_field_not_found_error(client: Prisma) -> None:
    """The FieldNotFoundError is raised when an unknown field is passed to
    both queries and mutations.
    """
    with pytest.raises(FieldNotFoundError, match='bad_field'):
        await client.post.find_first(where={'bad_field': 'foo'})  # type: ignore

    with pytest.raises(FieldNotFoundError, match='foo'):
        await client.post.create(
            data={  # type: ignore
                'title': 'foo',
                'published': True,
                'foo': 'bar',
            }
        )

    with pytest.raises(FieldNotFoundError, match='foo'):
        await client.post.find_first(
            where={
                'author': {
                    'is': {
                        'foo': 'bar',
                    },
                },
            },
        )
