from typing import List
from datetime import datetime, timedelta

from prisma import Prisma


def _utcnow() -> datetime:
    # workaround for https://github.com/RobertCraigie/prisma-client-py/issues/129
    now = datetime.utcnow()
    return now.replace(microsecond=int(now.microsecond / 1000) * 1000)


def _assert_datelist_equal(actual: List[datetime], expected: List[datetime]) -> None:
    actual = [dt.replace(tzinfo=None) for dt in actual]
    expected = [dt.replace(tzinfo=None) for dt in expected]
    assert actual == expected


def test_pushing_datetime(client: Prisma) -> None:
    """Pushing a DateTime[] value"""
    now = _utcnow()
    models = [
        client.lists.create({}),
        client.lists.create(
            data={
                'dates': [now, now + timedelta(hours=3)],
            },
        ),
    ]

    model = client.lists.update(
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

    model = client.lists.update(
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
    _assert_datelist_equal(model.dates, [now, now + timedelta(hours=3), now + timedelta(hours=7)])
