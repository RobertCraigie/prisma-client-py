from decimal import Decimal

from prisma import Prisma


def test_updating_decimal(client: Prisma) -> None:
    """Updating a Decimal[] value"""
    models = [
        client.lists.create({}),
        client.lists.create(
            data={
                'decimals': [Decimal('22.99'), Decimal('30.01')],
            },
        ),
    ]

    model = client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'decimals': {
                'set': [Decimal('3')],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal('3')]

    model = client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'decimals': [Decimal('7')],
        },
    )
    assert model is not None
    assert model.decimals == [Decimal('7')]


def test_filtering_decimal(client: Prisma) -> None:
    """Searching for records by a Decimal[] value"""
    with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'decimals': [],
            },
        )
        batcher.lists.create(
            data={
                'decimals': [Decimal('1'), Decimal('2')],
            },
        )

    model = client.lists.find_first(
        where={
            'decimals': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.decimals == []

    model = client.lists.find_first(
        where={
            'decimals': {
                'equals': [Decimal('1'), Decimal('2')],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal(1), Decimal(2)]

    model = client.lists.find_first(
        where={
            'decimals': {
                'has': Decimal('1'),
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal(1), Decimal(2)]

    model = client.lists.find_first(
        where={
            'decimals': {
                'has': Decimal(3),
            },
        },
    )
    assert model is None

    model = client.lists.find_first(
        where={
            'decimals': {
                'has_some': [Decimal(1), Decimal(3)],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal(1), Decimal(2)]

    model = client.lists.find_first(
        where={
            'decimals': {
                'has_every': [Decimal(1), Decimal(2), Decimal(3)],
            },
        },
    )
    assert model is None

    model = client.lists.find_first(
        where={
            'decimals': {
                'has_every': [Decimal(1)],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal(1), Decimal(2)]

    count = client.lists.count(
        where={
            'decimals': {
                'is_empty': True,
            },
        },
    )
    assert count == 1
