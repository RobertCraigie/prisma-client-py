from __future__ import annotations

import os
from pydantic import BaseModel

from .._types import DatabaseMapping
from .._compat import LiteralString


CURRENT_DATABASE = os.environ['PRISMA_DATABASE']


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


_mysql_queries = RawQueries(
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
)

_postgresql_queries = RawQueries(
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
)

RAW_QUERIES_MAPPING: DatabaseMapping[RawQueries] = {
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
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
}
