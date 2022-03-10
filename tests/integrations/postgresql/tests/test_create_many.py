import pytest
import prisma
from prisma import Prisma
from prisma.enums import Role


@pytest.mark.asyncio
async def test_create_many(client: Prisma) -> None:
    """Standard usage"""
    total = await client.user.create_many(
        [{'name': 'Robert', 'role': Role.ADMIN}, {'name': 'Tegan'}]
    )
    assert total == 2

    user = await client.user.find_first(where={'name': 'Robert'})
    assert user is not None
    assert user.name == 'Robert'
    assert user.role == Role.ADMIN

    assert await client.user.count() == 2


@pytest.mark.asyncio
async def test_skip_duplicates(client: Prisma) -> None:
    """Skipping duplcates ignores unique constraint errors"""
    user = await client.user.create({'name': 'Robert'})

    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        await client.user.create_many([{'id': user.id, 'name': 'Robert 2'}])

    assert exc.match(r'Unique constraint failed on the fields: \(`id`\)')

    count = await client.user.create_many(
        [{'id': user.id, 'name': 'Robert 2'}, {'name': 'Tegan'}],
        skip_duplicates=True,
    )
    assert count == 1
