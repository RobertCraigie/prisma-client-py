import pytest

import prisma
from prisma import Prisma


@pytest.mark.asyncio
async def test_create_many_skip_duplicates(client: Prisma) -> None:
    """Skipping duplcates ignores unique constraint errors"""
    user = await client.user.create({'name': 'Robert'})

    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        await client.user.create_many([{'id': user.id, 'name': 'Robert 2'}])

    assert exc.match(r'Unique constraint failed')

    count = await client.user.create_many(
        [{'id': user.id, 'name': 'Robert 2'}, {'name': 'Tegan'}],
        skip_duplicates=True,
    )
    assert count == 1
