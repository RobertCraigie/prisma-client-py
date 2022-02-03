import pytest
from prisma import Prisma
from prisma.enums import Role


@pytest.mark.asyncio
async def test_enum_create(client: Prisma) -> None:
    """Creating a record with an enum value"""
    user = await client.user.create({'name': 'Robert'})
    assert user.role == Role.USER

    user = await client.user.create({'name': 'Tegan', 'role': Role.ADMIN})
    assert user.role == Role.ADMIN
