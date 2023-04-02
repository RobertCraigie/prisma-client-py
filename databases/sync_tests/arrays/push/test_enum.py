from prisma import Prisma
from prisma.enums import Role


def test_pushing_enum(client: Prisma) -> None:
    """Pushing a Role[] enum value"""
    models = [
        client.lists.create({}),
        client.lists.create(
            data={
                'roles': [Role.USER, Role.ADMIN],
            },
        ),
    ]

    model = client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'roles': {
                'push': [Role.ADMIN, Role.USER],
            },
        },
    )
    assert model is not None
    assert model.roles == [Role.ADMIN, Role.USER]

    model = client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'roles': {
                'push': [Role.EDITOR],
            },
        },
    )
    assert model is not None
    assert model.roles == [Role.USER, Role.ADMIN, Role.EDITOR]
