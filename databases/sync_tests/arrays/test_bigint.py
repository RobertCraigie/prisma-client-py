from prisma import Prisma


def test_updating_bigints(client: Prisma) -> None:
    """Updating a BigInt[] value"""
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
            'id': models[1].id,
        },
        data={
            'bigints': {
                'set': [129003276736659456],
            },
        },
    )
    assert model is not None
    assert model.bigints == [129003276736659456]

    model = client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bigints': [298490675715112960],
        },
    )
    assert model is not None
    assert model.bigints == [298490675715112960]


def test_filtering_bigints(client: Prisma) -> None:
    """Searching for records by a BigInt[] value"""
    with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'bigints': [],
            },
        )
        batcher.lists.create(
            data={
                'bigints': [1, 2, 3],
            },
        )

    model = client.lists.find_first(
        where={
            'bigints': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.bigints == []

    model = client.lists.find_first(
        where={
            'bigints': {
                'equals': [1, 2, 3],
            },
        },
    )
    assert model is not None
    assert model.bigints == [1, 2, 3]

    model = client.lists.find_first(
        where={
            'bigints': {
                'has': 1,
            },
        },
    )
    assert model is not None
    assert model.bigints == [1, 2, 3]

    model = client.lists.find_first(
        where={
            'bigints': {
                'has': 4,
            },
        },
    )
    assert model is None

    model = client.lists.find_first(
        where={
            'bigints': {
                'has_some': [2, 3, 4],
            },
        },
    )
    assert model is not None
    assert model.bigints == [1, 2, 3]

    model = client.lists.find_first(
        where={
            'bigints': {
                'has_every': [2, 3, 4],
            },
        },
    )
    assert model is None

    model = client.lists.find_first(
        where={
            'bigints': {
                'has_every': [1, 2],
            },
        },
    )
    assert model is not None
    assert model.bigints == [1, 2, 3]

    count = client.lists.count(
        where={
            'bigints': {
                'is_empty': True,
            },
        },
    )
    assert count == 1
