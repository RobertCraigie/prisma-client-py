from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Union,
    Callable,
    Iterable,
    Optional,
    cast,
)
from datetime import datetime, timezone

import pytest_asyncio

if TYPE_CHECKING:
    from _pytest.scope import _ScopeName
    from _pytest.config import Config
    from _pytest.fixtures import FixtureFunctionMarker


# TODO: report pyright error to pytest-asyncio
def async_fixture(
    scope: Union[_ScopeName, Callable[[str, Config], _ScopeName]] = 'function',
    params: Optional[Iterable[object]] = None,
    autouse: bool = False,
    ids: Optional[
        Union[
            Iterable[Union[None, str, float, int, bool]],
            Callable[[Any], Optional[object]],
        ]
    ] = None,
    name: Optional[str] = None,
) -> FixtureFunctionMarker:
    """Wrapper over pytest_asyncio.fixture providing type hints"""
    return cast(
        'FixtureFunctionMarker',
        pytest_asyncio.fixture(  # pyright: reportUnknownMemberType=false
            None,
            scope=scope,
            params=params,
            autouse=autouse,
            ids=ids,
            name=name,
        ),
    )


def assert_similar_time(dt1: datetime, dt2: datetime, threshold: float = 0.5) -> None:
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


def assert_time_like_now(dt: datetime, threshold: int = 10) -> None:
    delta = datetime.now(timezone.utc) - dt
    assert delta.days == 0
    assert delta.total_seconds() < threshold
