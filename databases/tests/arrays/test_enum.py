import pytest

from prisma import Prisma
from prisma.enums import Role


@pytest.mark.asyncio
async def test_filtering_enums(client: Prisma) -> None:
    """Searching for records by a Role[] enum value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'roles': [],
            },
        )
        batcher.lists.create(
            data={
                'roles': [Role.USER, Role.ADMIN],
            },
        )

    model = await client.lists.find_first(
        where={
            'roles': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.roles == []

    model = await client.lists.find_first(
        where={
            'roles': {
                'equals': [Role.USER, Role.ADMIN],
            },
        },
    )
    assert model is not None
    assert model.roles == [Role.USER, Role.ADMIN]

    model = await client.lists.find_first(
        where={
            'roles': {
                'has': Role.ADMIN,
            },
        },
    )
    assert model is not None
    assert model.roles == [Role.USER, Role.ADMIN]

    model = await client.lists.find_first(
        where={
            'roles': {
                'has': Role.EDITOR,
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'roles': {
                'has_some': [Role.USER, Role.EDITOR],
            },
        },
    )
    assert model is not None
    assert model.roles == [Role.USER, Role.ADMIN]

    model = await client.lists.find_first(
        where={
            'roles': {
                'has_every': [Role.USER, Role.ADMIN, Role.EDITOR],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'roles': {
                'has_every': [Role.USER],
            },
        },
    )
    assert model is not None
    assert model.roles == [Role.USER, Role.ADMIN]

    count = await client.lists.count(
        where={
            'roles': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_updating_enum(client: Prisma) -> None:
    """Updating a Role[] enum value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'roles': [Role.USER, Role.ADMIN],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'roles': {
                'set': [Role.USER],
            },
        },
    )
    assert model is not None
    assert model.roles == [Role.USER]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'roles': [Role.ADMIN],
        },
    )
    assert model is not None
    assert model.roles == [Role.ADMIN]
