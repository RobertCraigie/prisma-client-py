from dirty_equals import IsPartialDict
import pytest

from prisma import Prisma
from prisma.enums import Role
from prisma.models import Types


@pytest.mark.asyncio
async def test_enum_create(client: Prisma) -> None:
    """Creating a record with an enum value"""
    record = await client.types.create({})
    assert record.enum == Role.USER

    record = await client.types.create({'enum': Role.ADMIN})
    assert record.enum == Role.ADMIN


# TODO: all other actions


def test_json_schema() -> None:
    """Ensure a JSON Schema definition can be created"""
    assert Types.schema() == IsPartialDict(
        definitions={
            'Role': {
                'title': 'Role',
                'description': 'An enumeration.',
                'enum': ['USER', 'ADMIN', 'EDITOR'],
                'type': 'string',
            }
        },
        properties=IsPartialDict(
            {
                'enum': {
                    '$ref': '#/definitions/Role',
                }
            }
        ),
    )
