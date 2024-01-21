from __future__ import annotations

import os
from typing import Set
from pathlib import Path
from typing_extensions import Literal, get_args, override

from pydantic import BaseModel
from syrupy.extensions.amber import AmberSnapshotExtension

from ._types import DatabaseMapping
from ._compat import LiteralString

DatabaseFeature = Literal[
    'enum',
    'json',
    'date',
    'arrays',
    'array_push',
    'json_arrays',
    'raw_queries',
    'create_many',
    'transactions',
    'case_sensitivity',
]


class DatabaseConfig(BaseModel):
    id: str
    name: str
    env_var: str
    bools_are_ints: bool
    autoincrement_id: str
    unsupported_features: Set[DatabaseFeature]
    default_date_func: str

    # TODO: run this under coverage
    def supports_feature(self, feature: DatabaseFeature) -> bool:  # pragma: no cover
        if feature not in get_args(DatabaseFeature):
            raise RuntimeError(f'Unknown feature: {feature}')

        return feature not in self.unsupported_features


# ------------------ Test helpers ------------------

from .constants import (
    TESTS_DIR,
    SYNC_TESTS_DIR,
)

SHARED_SNAPSHOTS_DIR = Path(__file__).parent.joinpath('__shared_snapshots__')
CURRENT_DATABASE = os.environ.get('PRISMA_DATABASE')


class AmberSharedExtension(AmberSnapshotExtension):
    """Syrupy extension that stores the snapshots in a parent __shared_snapshots__ dir"""

    @property
    @override
    def _dirname(self) -> str:
        test_dir = Path(self.test_location.filepath).parent
        if test_dir.is_relative_to(SYNC_TESTS_DIR):
            rel_dir = test_dir.relative_to(SYNC_TESTS_DIR)
        else:
            rel_dir = test_dir.relative_to(TESTS_DIR)

        return str(SHARED_SNAPSHOTS_DIR.joinpath(rel_dir))


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
