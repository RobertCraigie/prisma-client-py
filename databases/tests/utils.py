from __future__ import annotations

from typing import TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from typing_extensions import LiteralString
else:
    # for pydantic support
    LiteralString = str


class RawQueries(BaseModel):
    """Raw queries defined globally so they can be easily referenced in test functions"""

    count_posts: LiteralString

    find_user_by_id: LiteralString
    find_user_by_id_limit_1: LiteralString

    find_post_by_id: LiteralString
    find_posts_not_published: LiteralString

    select_unknown_table: LiteralString
    update_unique_post_title: LiteralString
    update_unique_post_new_title: LiteralString
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
        find_user_by_id_limit_1="""
            SELECT *
            FROM "User"
            WHERE "User".id = $1
            LIMIT 1
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
        update_unique_post_new_title="""
            UPDATE "Post"
            SET title = 'My new title'
            WHERE id = $1
        """,
        test_execute_raw_no_result="""
            UPDATE "Post"
            SET title = 'updated title'
            WHERE id = 'sdldsd'
        """,
    ),
    'mysql': RawQueries(
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
        find_user_by_id_limit_1="""
            SELECT *
            FROM User
            WHERE User.id = ?
            LIMIT 1
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
        update_unique_post_new_title="""
            UPDATE Post
            SET title = 'My new title'
            WHERE id = ?
        """,
        test_execute_raw_no_result="""
            UPDATE Post
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
        find_user_by_id_limit_1="""
            SELECT *
            FROM User
            WHERE User.id = ?
            LIMIT 1
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
        update_unique_post_new_title="""
            UPDATE Post
            SET title = 'My new title'
            WHERE id = ?
        """,
        test_execute_raw_no_result="""
            UPDATE Post
            SET title = 'updated title'
            WHERE id = 'sdldsd'
        """,
    ),
    'sqlserver': RawQueries(
        count_posts="""
            SELECT COUNT(*) as count
            FROM Post
        """,
        find_post_by_id="""
            SELECT *
            FROM Post
            WHERE id = @P1
        """,
        find_user_by_id="""
            SELECT *
            FROM User
            WHERE User.id = @P1
        """,
        find_user_by_id_limit_1="""
            SELECT *
            FROM User
            WHERE User.id = @P1
            LIMIT 1
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
            WHERE id = @P1
        """,
        update_unique_post_new_title="""
            UPDATE Post
            SET title = 'My new title'
            WHERE id = @P1
        """,
        test_execute_raw_no_result="""
            UPDATE Post
            SET title = 'updated title'
            WHERE id = 'sdldsd'
        """,
    ),
}
