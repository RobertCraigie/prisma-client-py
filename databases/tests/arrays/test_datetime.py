from typing import List
from datetime import datetime, timezone, timedelta

import pytest

from prisma import Prisma


def _utcnow() -> datetime:
    # workaround for https://github.com/RobertCraigie/prisma-client-py/issues/129
    now = datetime.now(timezone.utc)
    return now.replace(microsecond=int(now.microsecond / 1000) * 1000)


def _assert_datelist_equal(actual: List[datetime], expected: List[datetime]) -> None:
    actual = [dt.replace(tzinfo=None) for dt in actual]
    expected = [dt.replace(tzinfo=None) for dt in expected]
    assert actual == expected


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
