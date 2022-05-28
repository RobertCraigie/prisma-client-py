from __future__ import annotations

from typing import (
    Any,
    Union,
    Callable,
    Iterable,
    Optional,
    TYPE_CHECKING,
    cast,
)
from datetime import datetime, timezone

import pytest_asyncio
from pydantic import BaseModel

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.fixtures import FixtureFunctionMarker, _Scope
    from typing_extensions import LiteralString
else:
    # for pydantic support
    LiteralString = str


# TODO: proper solution for sharing test utilities between databases tests and core tests


class RawQueries(BaseModel):
    count_posts: LiteralString
    find_user_by_id: LiteralString
    find_post_by_id: LiteralString
    select_unknown_table: LiteralString
    find_posts_not_published: LiteralString
    update_unique_post_title: LiteralString
    test_query_raw_no_result: LiteralString
    test_execute_raw_no_result: LiteralString


RAW_QUERIES_MAPPING: dict[str, RawQueries] = {
    'postgresql': RawQueries(
        count_posts="""
            SELECT COUNT(*) as count
            FROM "Post"
        """,
        find_post_by_id="""
            SELECT *
            FROM "Post"
            WHERE id = $1
        """,
        find_user_by_id="""
            SELECT *
            FROM "User"
            WHERE "User".id = $1
        """,
        select_unknown_table="""
            SELECT *
            FROM bad_table;
        """,
        find_posts_not_published="""
            SELECT id, published
            FROM "Post"
            WHERE published = false
        """,
        test_query_raw_no_result="""
            SELECT *
            FROM "Post"
            WHERE id = 'sdldsd'
        """,
        update_unique_post_title="""
            UPDATE "Post"
            SET title = 'My edited title'
            WHERE id = $1
        """,
        test_execute_raw_no_result="""
            UPDATE "Post"
            SET title = 'updated title'
            WHERE id = 'sdldsd'
        """,
    ),
    'sqlite': RawQueries(
        count_posts="""
            SELECT COUNT(*) as count
            FROM Post
        """,
        find_post_by_id="""
            SELECT *
            FROM Post
            WHERE id = ?
        """,
        find_user_by_id="""
            SELECT *
            FROM User
            WHERE User.id = ?
        """,
        select_unknown_table="""
            SELECT *
            FROM bad_table;
        """,
        find_posts_not_published="""
            SELECT id, published
            FROM Post
            WHERE published = false
        """,
        test_query_raw_no_result="""
            SELECT *
            FROM Post
            WHERE id = 'sdldsd'
        """,
        update_unique_post_title="""
            UPDATE Post
            SET title = 'My edited title'
            WHERE id = ?
        """,
        test_execute_raw_no_result="""
            UPDATE Post
            SET title = 'updated title'
            WHERE id = 'sdldsd'
        """,
    ),
}


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


def assert_time_like_now(dt: datetime, threshold: int = 10) -> None:
    delta = datetime.now(timezone.utc) - dt
    assert delta.days == 0
    assert delta.total_seconds() < threshold


def async_fixture(
    scope: 'Union[_Scope, Callable[[str, Config], _Scope]]' = 'function',
    params: Optional[Iterable[object]] = None,
    autouse: bool = False,
    ids: Optional[
        Union[
            Iterable[Union[None, str, float, int, bool]],
            Callable[[Any], Optional[object]],
        ]
    ] = None,
    name: Optional[str] = None,
) -> 'FixtureFunctionMarker':
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
