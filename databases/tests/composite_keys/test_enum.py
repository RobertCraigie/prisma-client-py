import pytest

from prisma import Prisma
from prisma.enums import Role


@pytest.mark.asyncio
async def test_id5(client: Prisma) -> None:
    """Combined ID constraint with an Enum field"""
    model = await client.id5.create(
        data={
            'name': 'Robert',
            'role': Role.ADMIN,
        },
    )

    found = await client.id5.find_unique(
        where={
            'name_role': {
                'name': 'Robert',
                'role': Role.ADMIN,
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.role == Role.ADMIN

    found = await client.id5.find_unique(
        where={
            'name_role': {
                'name': 'Robert',
                'role': Role.USER,
            },
        },
    )
    assert found is None


@pytest.mark.asyncio
async def test_unique6(client: Prisma) -> None:
    """Combined unique constraint with an Enum field"""
    model = await client.unique6.create(
        data={
            'name': 'Robert',
            'role': Role.ADMIN,
        },
    )

    found = await client.unique6.find_unique(
        where={
            'name_role': {
                'name': 'Robert',
                'role': Role.ADMIN,
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.role == Role.ADMIN

    found = await client.unique6.find_unique(
        where={
            'name_role': {
                'name': 'Robert',
                'role': Role.USER,
            },
        },
    )
    assert found is None
