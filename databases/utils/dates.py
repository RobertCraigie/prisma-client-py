from datetime import datetime


# TODO: potentially remove this from tests/utils.py or normalise it


def assert_time_like_now(dt: datetime, threshold: int = 10) -> None:
    # NOTE: I do not know if prisma datetimes are always in UTC
    #
    # have to remove the timezone details as utcnow() is not timezone aware
    # and we cannot subtract a timezone aware datetime from a non timezone aware datetime
    dt = dt.replace(tzinfo=None)
    delta = datetime.utcnow() - dt
    assert delta.days == 0
    assert delta.total_seconds() < threshold


def assert_similar_time(
    dt1: datetime, dt2: datetime, threshold: float = 0.5
) -> None:
    """Assert the delta between the two datetimes is less than the given threshold (in seconds).

    This is required as there seems to be small data loss when marshalling and unmarshalling
    datetimes, for example:

    2021-09-26T15:00:18.708000+00:00 -> 2021-09-26T15:00:18.708776+00:00

    This issue does not appear to be solvable by us, please create an issue if you know of a solution.
    """
    if dt1 > dt2:
        delta = dt1 - dt2
    else:
        delta = dt2 - dt1

    assert delta.days == 0
    assert delta.total_seconds() < threshold
