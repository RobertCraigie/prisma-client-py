from dirty_equals import IsPartialDict

from prisma import Prisma
from prisma.enums import Role
from prisma.models import Types
from prisma._compat import PYDANTIC_V2, model_json_schema


def test_enum_create(client: Prisma) -> None:
    """Creating a record with an enum value"""
    record = client.types.create({})
    assert record.enum == Role.USER

    record = client.types.create({'enum': Role.ADMIN})
    assert record.enum == Role.ADMIN


# TODO: all other actions


def test_id5(client: Prisma) -> None:
    """Combined ID constraint with an Enum field"""
    model = client.id5.create(
        data={
            'name': 'Robert',
            'role': Role.ADMIN,
        },
    )

    found = client.id5.find_unique(
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

    found = client.id5.find_unique(
        where={
            'name_role': {
                'name': 'Robert',
                'role': Role.USER,
            },
        },
    )
    assert found is None


def test_unique6(client: Prisma) -> None:
    """Combined unique constraint with an Enum field"""
    model = client.unique6.create(
        data={
            'name': 'Robert',
            'role': Role.ADMIN,
        },
    )

    found = client.unique6.find_unique(
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

    found = client.unique6.find_unique(
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
