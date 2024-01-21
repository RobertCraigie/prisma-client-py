import pytest
from dirty_equals import IsPartialDict

from prisma import Prisma
from prisma.enums import Role
from prisma.models import Types
from prisma._compat import PYDANTIC_V2, model_json_schema


@pytest.mark.asyncio
async def test_enum_create(client: Prisma) -> None:
    """Creating a record with an enum value"""
    record = await client.types.create({})
    assert record.enum == Role.USER

    record = await client.types.create({'enum': Role.ADMIN})
    assert record.enum == Role.ADMIN

    # ensure consistent format
    assert str(record.enum) == 'ADMIN'
    assert f'{record.enum}' == 'ADMIN'
    assert '%s' % record.enum == 'ADMIN'

    assert str(Role.ADMIN) == 'ADMIN'
    assert f'{Role.ADMIN}' == 'ADMIN'
    assert '%s' % Role.ADMIN == 'ADMIN'


# TODO: all other actions


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


def test_json_schema() -> None:
    """Ensure a JSON Schema definition can be created"""
    defs = {
        'Role': IsPartialDict(
            {
                'title': 'Role',
                'enum': ['USER', 'ADMIN', 'EDITOR'],
                'type': 'string',
            }
        )
    }

    if PYDANTIC_V2:
        assert model_json_schema(Types) == IsPartialDict(
            {
                '$defs': defs,
                'properties': IsPartialDict(
                    {
                        'enum': {
                            '$ref': '#/$defs/Role',
                        }
                    }
                ),
            },
        )
    else:
        assert model_json_schema(Types) == IsPartialDict(
            definitions=defs,
            properties=IsPartialDict(
                {
                    'enum': {
                        '$ref': '#/definitions/Role',
                    }
                }
            ),
        )
