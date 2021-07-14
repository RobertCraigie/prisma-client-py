import pytest
from prisma import Client
from prisma.types import RoleEnum


@pytest.mark.asyncio
async def test_enum_create(client: Client) -> None:
    user = await client.user.create({'name': 'Robert'})
    assert user.role == RoleEnum.USER

    user = await client.user.create({'name': 'Tegan', 'role': RoleEnum.ADMIN})
    assert user.role == RoleEnum.ADMIN

    user = await client.user.create({'name': 'Bob', 'role': RoleEnum.ADMIN.value})
    assert user.role == RoleEnum.ADMIN
