from typing import Optional, cast

import pytest
from pydantic import BaseModel

from prisma import Prisma

from .._types import DatabaseMapping, SupportedDatabase


# Define a class to hold the search queries
class FullTextSearchSyntax(BaseModel):
    search_or: str
    search_and: str


# Define the queries for MySQL
_mysql_syntax = FullTextSearchSyntax(
    search_or='cats dogs',
    search_and='+cats +dogs',
)

# Define the queries for PostgreSQL
_postgresql_syntax = FullTextSearchSyntax(
    search_or='cats | dogs',
    search_and='cats & dogs',
)

# Map the syntax to the corresponding database
FULL_TEXT_SEARCH_SYNTAX: DatabaseMapping[Optional[FullTextSearchSyntax]] = {
    'mysql': _mysql_syntax,
    'postgresql': _postgresql_syntax,
    'cockroachdb': None,
    'mariadb': None,
    'sqlite': None,
}


def test_full_text_search(client: Prisma) -> None:
    """Ensure that full-text search works correctly on both PostgreSQL and MySQL"""

    # Determine the correct syntax based on the database
    db_type = cast(SupportedDatabase, client._active_provider)
    syntax = FULL_TEXT_SEARCH_SYNTAX[db_type]

    if syntax is None:
        pytest.skip(f'Skipping test for {db_type}')

    # Create some posts with varied content
    client.post.create_many(
        data=[
            {
                'title': 'cats are great pets. dogs are loyal companions.',
                'published': True,
            },
            {
                'title': 'cats are independent and mysterious animals.',
                'published': True,
            },
            {
                'title': 'rabbits and hamsters are small and cute pets.',
                'published': True,
            },
        ]
    )

    # Test: Search for posts that contain 'cats' or 'dogs'
    posts = client.post.find_many(
        where={
            'title': {
                'search': syntax.search_or,
            },
        }
    )
    assert len(posts) == 2
    assert any('cats' in post.title for post in posts)
    assert any('dogs' in post.title for post in posts)

    # Test: Search for posts that contain both 'cats' and 'dogs'
    posts = client.post.find_many(
        where={
            'title': {
                'search': syntax.search_and,
            },
        }
    )
    assert len(posts) == 1
    assert 'cats' in posts[0].title
    assert 'dogs' in posts[0].title


def test_order_by_relevance(client: Prisma) -> None:
    """Ensure that ordering by relevance works correctly on both PostgreSQL and MySQL"""

    # Determine the correct syntax based on the database
    db_type = cast(SupportedDatabase, client._active_provider)
    syntax = FULL_TEXT_SEARCH_SYNTAX[db_type]

    if syntax is None:
        pytest.skip(f'Skipping test for {db_type}')

    # Create some posts with varied content
    client.post.create_many(
        data=[
            {
                'title': 'cats are great pets. dogs are loyal companions.',
                'published': True,
            },
            {
                'title': 'cats are independent and mysterious animals.',
                'published': True,
            },
            {
                'title': 'rabbits and hamsters are small and cute pets.',
                'published': True,
            },
        ]
    )

    # Test: Order posts by relevance descending
    posts = client.post.find_first(
        order={
            '_relevance': {
                'fields': ['title'],
                'search': syntax.search_or,
                'sort': 'desc',
            },
        }
    )
    assert posts is not None
    assert 'cats' in posts.title
    assert 'dogs' in posts.title

    # Test: Order posts by relevance ascending
    posts = client.post.find_first(
        order={
            '_relevance': {
                'fields': ['title'],
                'search': syntax.search_or,
                'sort': 'asc',
            },
        }
    )
    assert posts is not None
    assert 'rabbits' in posts.title
