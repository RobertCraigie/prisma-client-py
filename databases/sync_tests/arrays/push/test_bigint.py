from prisma import Prisma


def test_pushing_bigints(client: Prisma) -> None:
    """Pushing values to a BigInt[] field"""
    models = [
        client.lists.create({}),
        client.lists.create(
            data={
                'bigints': [539506179039297536, 281454500584095754],
            },
        ),
    ]

    model = client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'bigints': {
                'push': [538075535121842179],
            },
        },
    )
    assert model is not None
    assert model.bigints == [538075535121842179]

    model = client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bigints': {
                'push': [186214420957888512],
            },
        },
    )
    assert model is not None
    assert model.bigints == [
        539506179039297536,
        281454500584095754,
        186214420957888512,
    ]
