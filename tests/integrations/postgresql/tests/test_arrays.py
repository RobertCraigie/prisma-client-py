from datetime import datetime, timedelta
from typing import Any, List

import pytest
from prisma import Prisma, Json, Base64
from prisma.enums import Role
from prisma.models import Lists


def _utcnow() -> datetime:
    # workaround for https://github.com/RobertCraigie/prisma-client-py/issues/129
    now = datetime.utcnow()
    return now.replace(microsecond=int(now.microsecond / 1000) * 1000)


def _assert_datelist_equal(
    actual: List[datetime], expected: List[datetime]
) -> None:
    actual = [dt.replace(tzinfo=None) for dt in actual]
    expected = [dt.replace(tzinfo=None) for dt in expected]
    assert actual == expected


@pytest.mark.asyncio
async def test_order_by(client: Prisma) -> None:
    """Results can be ordered by a String[] field"""
    total = await client.lists.create_many(
        [
            {'id': 'a', 'strings': ['a', 'b']},
            {'id': 'b', 'strings': ['c']},
        ],
    )
    assert total == 2

    models = await client.lists.find_many(order={'strings': 'desc'})
    assert len(models) == 2
    assert models[0].id == 'b'
    assert models[1].id == 'a'

    models = await client.lists.find_many(order={'strings': 'asc'})
    assert len(models) == 2
    assert models[0].id == 'a'
    assert models[1].id == 'b'


@pytest.mark.asyncio
async def test_update_many(client: Prisma) -> None:
    """Updating many String[] values"""
    result = await client.lists.create_many(
        [
            {'id': 'a', 'strings': ['foo']},
            {'id': 'b', 'strings': ['bar']},
        ]
    )
    assert result == 2

    result = await client.lists.update_many(
        where={},
        data={
            'strings': {
                'set': ['foo'],
            },
        },
    )
    assert result == 2

    model = await client.lists.find_unique(
        where={
            'id': 'a',
        },
    )
    assert model is not None
    assert model.strings == ['foo']


# NOTE: a lot of these tests are copied and pasted, this is because there are subtle differences
# that we have to change when testing different types, I do not care about duplicating code when
# it comes to writing tests and while it would be possible to refactor these to use pytest.parametrize
# it would make the tests much less readable and much more difficult to understand.


@pytest.mark.asyncio
async def test_updating_strings(client: Prisma) -> None:
    """Updating a String[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'strings': ['a', 'b', 'c'],
            },
        ),
    ]

    model = await client.lists.update(
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

    model = await client.lists.update(
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

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'strings': {
                'set': ['e'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['e']

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'strings': ['f'],
        },
    )
    assert model is not None
    assert model.strings == ['f']


@pytest.mark.asyncio
async def test_updating_bytes(client: Prisma) -> None:
    """Updating a Bytes[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'bytes': [Base64.encode(b'foo'), Base64.encode(b'bar')],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'bytes': {
                'push': [Base64.encode(b'a'), Base64.encode(b'b')],
            },
        },
    )
    assert model is not None
    assert model.bytes == [Base64.encode(b'a'), Base64.encode(b'b')]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bytes': {
                'push': [Base64.encode(b'baz')],
            },
        },
    )
    assert model is not None
    assert model.bytes == [
        Base64.encode(b'foo'),
        Base64.encode(b'bar'),
        Base64.encode(b'baz'),
    ]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bytes': {
                'set': [Base64.encode(b'd')],
            },
        },
    )
    assert model is not None
    assert model.bytes == [Base64.encode(b'd')]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bytes': [Base64.encode(b'e')],
        },
    )
    assert model is not None
    assert model.bytes == [Base64.encode(b'e')]


@pytest.mark.asyncio
async def test_updating_datetime(client: Prisma) -> None:
    """Updating a DateTime[] value"""
    now = _utcnow()
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'dates': [now, now + timedelta(hours=3)],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'dates': {
                'push': [now, now + timedelta(days=5)],
            },
        },
    )
    assert model is not None
    _assert_datelist_equal(model.dates, [now, now + timedelta(days=5)])

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'dates': {
                'push': [now + timedelta(hours=7)],
            },
        },
    )
    assert model is not None
    _assert_datelist_equal(
        model.dates, [now, now + timedelta(hours=3), now + timedelta(hours=7)]
    )

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'dates': {
                'set': [now + timedelta(days=999)],
            },
        },
    )
    assert model is not None
    _assert_datelist_equal(model.dates, [now + timedelta(days=999)])

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'dates': [now + timedelta(hours=999)],
        },
    )
    assert model is not None
    _assert_datelist_equal(model.dates, [now + timedelta(hours=999)])


@pytest.mark.asyncio
async def test_updating_boolean(client: Prisma) -> None:
    """Updating a Boolean[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'bools': [False, True],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'bools': {
                'push': [True, False, True],
            },
        },
    )
    assert model is not None
    assert model.bools == [True, False, True]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bools': {
                'push': [False],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True, False]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bools': {
                'set': [False],
            },
        },
    )
    assert model is not None
    assert model.bools == [False]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bools': [True],
        },
    )
    assert model is not None
    assert model.bools == [True]


@pytest.mark.asyncio
async def test_updating_ints(client: Prisma) -> None:
    """Updating a Int[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'ints': [1, 2, 3],
            },
        ),
    ]

    model = await client.lists.update(
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

    model = await client.lists.update(
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

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'ints': {
                'set': [5],
            },
        },
    )
    assert model is not None
    assert model.ints == [5]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'ints': [6],
        },
    )
    assert model is not None
    assert model.ints == [6]


@pytest.mark.asyncio
async def test_updating_bigints(client: Prisma) -> None:
    """Updating a BigInt[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'bigints': [539506179039297536, 281454500584095754],
            },
        ),
    ]

    model = await client.lists.update(
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

    model = await client.lists.update(
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

    model = await client.lists.update(
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

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bigints': [298490675715112960],
        },
    )
    assert model is not None
    assert model.bigints == [298490675715112960]


@pytest.mark.asyncio
async def test_updating_floats(client: Prisma) -> None:
    """Updating a Float[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'floats': [3.4, 6.8, 12.4],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'floats': {
                'push': [102.3, 500.7],
            },
        },
    )
    assert model is not None
    assert model.floats == [102.3, 500.7]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'floats': {
                'push': [20],
            },
        },
    )
    assert model is not None
    assert model.floats == [3.4, 6.8, 12.4, 20]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'floats': {
                'set': [99999.999],
            },
        },
    )
    assert model is not None
    assert model.floats == [99999.999]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'floats': [80],
        },
    )
    assert model is not None
    assert model.floats == [80]


@pytest.mark.asyncio
async def test_updating_json(client: Prisma) -> None:
    """Updating a Json[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'json_objects': [Json('foo'), Json(['foo', 'bar'])],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'json_objects': {
                'push': [Json.keys(foo='bar'), Json(True)],
            },
        },
    )
    assert model is not None
    assert model.json_objects == [{'foo': 'bar'}, True]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'json_objects': {
                'push': [Json('Baz')],
            },
        },
    )
    assert model is not None
    assert model.json_objects == ['foo', ['foo', 'bar'], 'Baz']

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'json_objects': {
                'set': [Json.keys(hello=123)],
            },
        },
    )
    assert model is not None
    assert model.json_objects == [{'hello': 123}]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'json_objects': [Json.keys(world=None)],
        },
    )
    assert model is not None
    assert model.json_objects == [{'world': None}]


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

    model = await client.lists.update(
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


@pytest.mark.asyncio
async def test_filtering_strings(client: Prisma) -> None:
    """Searching for records by a String[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'strings': [],
            },
        )
        batcher.lists.create(
            data={
                'strings': ['a', 'b', 'c'],
            },
        )

    model = await client.lists.find_first(
        where={
            'strings': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.strings == []  # TODO: document this behaviour

    model = await client.lists.find_first(
        where={
            'strings': {
                'equals': ['a', 'b', 'c'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    model = await client.lists.find_first(
        where={
            'strings': {
                'has': 'a',
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    model = await client.lists.find_first(
        where={
            'strings': {
                'has': 'd',
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'strings': {
                'has_some': ['b', 'c'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    model = await client.lists.find_first(
        where={
            'strings': {
                'has_every': ['b', 'c', 'd'],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'strings': {
                'has_every': ['a', 'b'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    count = await client.lists.count(
        where={
            'strings': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_filtering_bools(client: Prisma) -> None:
    """Searching for records by a Boolean[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'bools': [],
            },
        )
        batcher.lists.create(
            data={
                'bools': [False, True],
            },
        )

    model = await client.lists.find_first(
        where={
            'bools': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.bools == []

    model = await client.lists.find_first(
        where={
            'bools': {
                'equals': [],
            },
        },
    )
    assert model is not None
    assert model.bools == []

    model = await client.lists.find_first(
        where={
            'bools': {
                'equals': [False, True],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    model = await client.lists.find_first(
        where={
            'bools': {
                'has': True,
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    model = await client.lists.find_first(
        where={
            'bools': {
                'has_some': [True],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    model = await client.lists.find_first(
        where={
            'bools': {
                'has_every': [False, True, False, True],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    model = await client.lists.find_first(
        where={
            'bools': {
                'has_every': [False, True],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True]

    count = await client.lists.count(
        where={
            'bools': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_filtering_ints(client: Prisma) -> None:
    """Searching for records by a Int[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'ints': [],
            },
        )
        batcher.lists.create(
            data={
                'ints': [1, 2, 3],
            },
        )

    model = await client.lists.find_first(
        where={
            'ints': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.ints == []

    model = await client.lists.find_first(
        where={
            'ints': {
                'equals': [1, 2, 3],
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'ints': {
                'has': 1,
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'ints': {
                'has': 4,
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'ints': {
                'has_some': [2, 3, 4],
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'ints': {
                'has_every': [2, 3, 4],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'ints': {
                'has_every': [1, 2],
            },
        },
    )
    assert model is not None
    assert model.ints == [1, 2, 3]

    count = await client.lists.count(
        where={
            'ints': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_filtering_floats(client: Prisma) -> None:
    """Searching for records by a Float[] value"""
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'floats': [],
            },
        )
        batcher.lists.create(
            data={
                'floats': [1.3, 2.6, 3.9],
            },
        )

    model = await client.lists.find_first(
        where={
            'floats': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.floats == []

    model = await client.lists.find_first(
        where={
            'floats': {
                'equals': [1.3, 2.6, 3.9],
            },
        },
    )
    assert model is not None
    assert model.floats == [1.3, 2.6, 3.9]

    model = await client.lists.find_first(
        where={
            'floats': {
                'has': 2.6,
            },
        },
    )
    assert model is not None
    assert model.floats == [1.3, 2.6, 3.9]

    model = await client.lists.find_first(
        where={
            'floats': {
                'has': 4.0,
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'floats': {
                'has_some': [2.6, 3.9, 4.5],
            },
        },
    )
    assert model is not None
    assert model.floats == [1.3, 2.6, 3.9]

    model = await client.lists.find_first(
        where={
            'floats': {
                'has_every': [2.6, 3.9, 4.5],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'floats': {
                'has_every': [2.6, 3.9],
            },
        },
    )
    assert model is not None
    assert model.floats == [1.3, 2.6, 3.9]

    count = await client.lists.count(
        where={
            'floats': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_filtering_bigints(client: Prisma) -> None:
    """Searching for records by a BigInt[] value"""
    async with client.batch_() as batcher:
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

    model = await client.lists.find_first(
        where={
            'bigints': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.bigints == []

    model = await client.lists.find_first(
        where={
            'bigints': {
                'equals': [1, 2, 3],
            },
        },
    )
    assert model is not None
    assert model.bigints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'bigints': {
                'has': 1,
            },
        },
    )
    assert model is not None
    assert model.bigints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'bigints': {
                'has': 4,
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'bigints': {
                'has_some': [2, 3, 4],
            },
        },
    )
    assert model is not None
    assert model.bigints == [1, 2, 3]

    model = await client.lists.find_first(
        where={
            'bigints': {
                'has_every': [2, 3, 4],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'bigints': {
                'has_every': [1, 2],
            },
        },
    )
    assert model is not None
    assert model.bigints == [1, 2, 3]

    count = await client.lists.count(
        where={
            'bigints': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_filtering_json(client: Prisma) -> None:
    """Searching for records by a Json[] value"""
    expected_raw: List[Any] = [[], {'country': 'Scotland'}]
    expected_objects = [Json([]), Json.keys(country='Scotland')]

    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'json_objects': [],
            },
        )
        batcher.lists.create(
            data={
                'json_objects': expected_objects,
            },
        )

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.json_objects == []

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'equals': expected_objects,
            },
        },
    )
    assert model is not None
    assert model.json_objects == expected_raw

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has': Json([]),
            },
        },
    )
    assert model is not None
    assert model.json_objects == expected_raw

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has': Json(['foo']),
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has_some': [*expected_objects, Json(['foo'])],
            },
        },
    )
    assert model is not None
    assert model.json_objects == expected_raw

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has_every': [*expected_objects, Json(['foo'])],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'json_objects': {
                'has_every': [*expected_objects[:2]],
            },
        },
    )
    assert model is not None
    assert model.json_objects == expected_raw

    count = await client.lists.count(
        where={
            'json_objects': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_filtering_datetime(client: Prisma) -> None:
    """Searching for records by a DateTime[] value"""
    now = _utcnow()
    expected_objects = [now, now + timedelta(hours=1)]
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'dates': [],
            },
        )
        batcher.lists.create(
            data={
                'dates': expected_objects,
            },
        )

    model = await client.lists.find_first(
        where={
            'dates': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.dates == []

    model = await client.lists.find_first(
        where={
            'dates': {
                'equals': expected_objects,
            },
        },
    )
    assert model is not None
    _assert_datelist_equal(model.dates, expected_objects)

    model = await client.lists.find_first(
        where={
            'dates': {
                'has': now,
            },
        },
    )
    assert model is not None
    _assert_datelist_equal(model.dates, expected_objects)

    model = await client.lists.find_first(
        where={
            'dates': {
                'has': now + timedelta(seconds=5),
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'dates': {
                'has_some': [*expected_objects, now + timedelta(seconds=5)],
            },
        },
    )
    assert model is not None
    _assert_datelist_equal(model.dates, expected_objects)

    model = await client.lists.find_first(
        where={
            'dates': {
                'has_every': [*expected_objects, now + timedelta(minutes=10)],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'dates': {
                'has_every': [*expected_objects[:2]],
            },
        },
    )
    assert model is not None
    _assert_datelist_equal(model.dates, expected_objects)

    count = await client.lists.count(
        where={
            'dates': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


@pytest.mark.asyncio
async def test_filtering_bytes(client: Prisma) -> None:
    """Searching for records by a Bytes[] value"""
    expected_objects = [Base64.encode(b'foo'), Base64.encode(b'bar')]
    async with client.batch_() as batcher:
        batcher.lists.create({})
        batcher.lists.create(
            data={
                'bytes': [],
            },
        )
        batcher.lists.create(
            data={
                'bytes': expected_objects,
            },
        )

    model = await client.lists.find_first(
        where={
            'bytes': {
                'equals': None,
            },
        },
    )
    assert model is not None
    assert model.bytes == []

    model = await client.lists.find_first(
        where={
            'bytes': {
                'equals': expected_objects,
            },
        },
    )
    assert model is not None
    assert model.bytes == expected_objects

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has': Base64.encode(b'foo'),
            },
        },
    )
    assert model is not None
    assert model.bytes == expected_objects

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has': Base64.encode(b'baz'),
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has_some': [*expected_objects, Base64.encode(b'fjhf')],
            },
        },
    )
    assert model is not None
    assert model.bytes == expected_objects

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has_every': [*expected_objects, Base64.encode(b'prisma')],
            },
        },
    )
    assert model is None

    model = await client.lists.find_first(
        where={
            'bytes': {
                'has_every': [*expected_objects[:2]],
            },
        },
    )
    assert model is not None
    assert model.bytes == expected_objects

    count = await client.lists.count(
        where={
            'bytes': {
                'is_empty': True,
            },
        },
    )
    assert count == 1


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
async def test_bytes_constructing(client: Prisma) -> None:
    """A list of Base64 fields can be passed to the model constructor"""
    record = await client.lists.create({})
    model = Lists.parse_obj(
        {
            **record.dict(),
            'bytes': [
                Base64.encode(b'foo'),
                Base64.encode(b'bar'),
            ],
        }
    )
    assert model.bytes == [Base64.encode(b'foo'), Base64.encode(b'bar')]
