from prisma import Prisma


def test_pushing_ints(client: Prisma) -> None:
    """Pushing an Int[] value"""
    models = [
        client.lists.create({}),
        client.lists.create(
            data={
                'ints': [1, 2, 3],
            },
        ),
    ]

    model = client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'ints': {
                'push': [1023023, 999],
            },
        },
    )
    assert model is not None
    assert model.ints == [1023023, 999]

    model = client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'ints': {
                'push': [4],
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3, 4]
