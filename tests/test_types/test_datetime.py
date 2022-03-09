import datetime
import pytest
from prisma import Prisma

from ..utils import assert_similar_time


@pytest.mark.asyncio
async def test_filtering(client: Prisma) -> None:
    """Finding records by a DateTime value"""
    now = datetime.datetime.now(datetime.timezone.utc)
    async with client.batch_() as batcher:
        for i in range(10):
            batcher.types.create(
                {'datetime': now + datetime.timedelta(hours=i)}
            )

    total = await client.types.count(
        where={'datetime': {'gte': now + datetime.timedelta(hours=5)}}
    )
    assert total == 5

    found = await client.types.find_first(
        where={
            'datetime': {
                'equals': now,
            },
        },
    )
    assert found is not None
    assert_similar_time(found.datetime, now)

    results = await client.types.find_many(
        where={
            'datetime': {
                'in': [
                    now + datetime.timedelta(hours=1),
                    now + datetime.timedelta(hours=4),
                    now + datetime.timedelta(hours=10),
                ],
            },
        },
        order={
            'datetime': 'asc',
        },
    )
    assert len(results) == 2
    assert_similar_time(results[0].datetime, now + datetime.timedelta(hours=1))
    assert_similar_time(results[1].datetime, now + datetime.timedelta(hours=4))

    found = await client.types.find_first(
        where={
            'datetime': {
                'not_in': [
                    now,
                    now + datetime.timedelta(hours=1),
                    now + datetime.timedelta(hours=2),
                ],
            },
        },
        order={
            'datetime': 'asc',
        },
    )
    assert found is not None
    assert_similar_time(found.datetime, now + datetime.timedelta(hours=3))

    found = await client.types.find_first(
        where={
            'datetime': {
                'lt': now + datetime.timedelta(hours=1),
            },
        },
        order={
            'datetime': 'desc',
        },
    )
    assert found is not None
    assert_similar_time(found.datetime, now)

    found = await client.types.find_first(
        where={
            'datetime': {
                'lte': now + datetime.timedelta(hours=1),
            },
        },
        order={
            'datetime': 'desc',
        },
    )
    assert found is not None
    assert_similar_time(found.datetime, now + datetime.timedelta(hours=1))

    found = await client.types.find_first(
        where={
            'datetime': {
                'gt': now,
            },
        },
        order={
            'datetime': 'asc',
        },
    )
    assert found is not None
    assert_similar_time(found.datetime, now + datetime.timedelta(hours=1))

    found = await client.types.find_first(
        where={
            'datetime': {
                'gte': now,
            },
        },
        order={
            'datetime': 'asc',
        },
    )
    assert found is not None
    assert_similar_time(found.datetime, now)

    found = await client.types.find_first(
        where={
            'datetime': {
                'not': now,
            },
        },
        order={
            'datetime': 'asc',
        },
    )
    assert found is not None
    assert_similar_time(found.datetime, now + datetime.timedelta(hours=1))

    found = await client.types.find_first(
        where={
            'datetime': {
                'not': {
                    'equals': now,
                },
            },
        },
        order={
            'datetime': 'asc',
        },
    )
    assert found is not None
    assert_similar_time(now + datetime.timedelta(hours=1), found.datetime)


@pytest.mark.asyncio
async def test_finds(client: Prisma) -> None:
    """Adding 1 second timedelta finds the record"""
    record = await client.types.create(data={})
    found = await client.types.find_first(
        where={
            'datetime': {
                'lt': record.datetime + datetime.timedelta(seconds=1),
            },
        },
    )
    assert found is not None
    assert found.id == record.id


@pytest.mark.asyncio
async def test_tz_aware(client: Prisma) -> None:
    """Modifying timezone still finds the record"""
    record = await client.types.create(data={})
    found = await client.types.find_first(
        where={
            'datetime': {
                'lt': (
                    record.datetime + datetime.timedelta(hours=1)
                ).astimezone(datetime.timezone.max)
            }
        }
    )
    assert found is not None
    assert found.id == record.id
