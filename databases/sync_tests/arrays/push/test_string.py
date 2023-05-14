from prisma import Prisma


def test_pushing_strings(client: Prisma) -> None:
    """Pushing a String[] value"""
    models = [
        client.lists.create({}),
        client.lists.create(
            data={
                'strings': ['a', 'b', 'c'],
            },
        ),
    ]

    model = client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'strings': {
                'push': ['a', 'B'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'B']

    model = client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'strings': {
                'push': ['d'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c', 'd']
