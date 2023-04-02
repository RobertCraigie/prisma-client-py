from prisma import Prisma


def test_filtering(client: Prisma) -> None:
    """Finding records by a Boolean value"""
    with client.batch_() as batcher:
        for i in range(10):
            batcher.types.create({'bool_': i % 2 == 0})

    total = client.types.count(where={'bool_': {'equals': True}})
    assert total == 5

    found = client.types.find_first(
        where={
            'bool_': {
                'equals': False,
            },
        },
    )
    assert found is not None
    assert found.bool_ is False

    found = client.types.find_first(
        where={
            'bool_': {
                'not': True,
            },
        },
    )
    assert found is not None
    assert found.bool_ is False

    found = client.types.find_first(
        where={
            'bool_': {
                'not': False,
            },
        },
    )
    assert found is not None
    assert found.bool_ is True

    found = client.types.find_first(
        where={
            'bool_': False,
        },
    )
    assert found is not None
    assert found.bool_ is False


def test_filtering_nulls(client: Prisma) -> None:
    """None is a valid filter for nullable Boolean fields"""
    client.types.create(
        {
            'string': 'a',
            'optional_bool': None,
        },
    )
    client.types.create(
        {
            'string': 'b',
            'optional_bool': True,
        },
    )
    client.types.create(
        {
            'string': 'c',
            'optional_bool': False,
        },
    )

    found = client.types.find_first(
        where={
            'NOT': [
                {
                    'optional_bool': None,
                },
            ],
        },
        order={
            'string': 'asc',
        },
    )
    assert found is not None
    assert found.string == 'b'
    assert found.optional_bool is True

    count = client.types.count(
        where={
            'optional_bool': None,
        },
    )
    assert count == 1

    count = client.types.count(
        where={
            'NOT': [
                {
                    'optional_bool': None,
                },
            ],
        },
    )
    assert count == 2
