import pytest
from prisma import Client
from prisma.enums import Role


@pytest.mark.asyncio
async def test_enum_create(client: Client) -> None:
    """Creating a record with an enum value"""
    user = await client.user.create({'name': 'Robert'})
    assert user.role == Role.USER

    user = await client.user.create({'name': 'Tegan', 'role': Role.ADMIN})
    assert user.role == Role.ADMIN
