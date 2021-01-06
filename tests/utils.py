import asyncio
from datetime import datetime
from typing import Coroutine, Any


def async_run(coro: Coroutine[Any, Any, Any]) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


def assert_time_like_now(dt: datetime, threshold: int = 10) -> None:
    # NOTE: I do not know if prisma datetimes are always in UTC
    #
    # have to remove the timezone details as utcnow() is not timezone aware
    # and we cannot subtract a timezone aware datetime from a non timezone aware datetime
    dt = dt.replace(tzinfo=None)
    delta = datetime.utcnow() - dt
    assert delta.days == 0
    assert delta.total_seconds() < threshold
