import pytest
from pydantic import BaseModel

from prisma import Prisma

from .._types import DatabaseMapping, SupportedDatabase


# Define a class to hold the search queries
class FullTextSearchSyntax(BaseModel):
    search_or: str
    search_and: str
    search_not: str
    search_phrase: str


# Define the queries for MySQL
_mysql_syntax = FullTextSearchSyntax(
    search_or='cats dogs',
    search_and='+cats +dogs',
    search_not='+cats -dogs',
    search_phrase='"small and cute"',
)

# Define the queries for PostgreSQL
_postgresql_syntax = FullTextSearchSyntax(
    search_or='cats | dogs',
    search_and='cats & dogs',
    search_not='cats & !dogs',
    search_phrase='small <-> cute',
)

# Map the syntax to the corresponding database
FULL_TEXT_SEARCH_SYNTAX: DatabaseMapping[FullTextSearchSyntax] = {
    'mysql': _mysql_syntax,
    'postgresql': _postgresql_syntax,
}


@pytest.mark.asyncio
async def test_full_text_search(client: Prisma) -> None:
    """Ensure that full-text search works correctly on both PostgreSQL and MySQL"""

    # Determine the correct syntax based on the database
    db_type: SupportedDatabase = client._active_provider
    syntax = FULL_TEXT_SEARCH_SYNTAX[db_type]

    # Create some posts with varied content
    client.post.create_many(
        data=[
            {
                'title': 'Post about cats and dogs',
                'body': 'Cats are great pets. Dogs are loyal companions.',
                'published': True,
            },
            {
                'title': 'Post about only cats',
                'body': 'Cats are independent and mysterious animals.',
                'published': True,
            },
            {
                'title': 'Post about other animals',
                'body': 'Rabbits and hamsters are small and cute pets.',
                'published': True,
            },
        ]
    )

    # Test: Search for posts that contain 'cats' or 'dogs'
    posts = client.post.find_many(
        where={
            'body': {
                'search': syntax.search_or,
            },
        }
    )
    assert len(posts) == 2
    assert any('cats' in post.body for post in posts)
    assert any('dogs' in post.body for post in posts)

    # Test: Search for posts that contain both 'cats' and 'dogs'
    posts = client.post.find_many(
        where={
            'body': {
                'search': syntax.search_and,
            },
        }
    )
    assert len(posts) == 1
    assert 'cats' in posts[0].body
    assert 'dogs' in posts[0].body

    # Test: Search for posts that contain 'cats' but not 'dogs'
    posts = client.post.find_many(
        where={
            'body': {
                'search': syntax.search_not,
            },
        }
    )
    assert len(posts) == 1
    assert 'cats' in posts[0].body
    assert 'dogs' not in posts[0].body

    # Test: Search for posts that contain the phrase 'small and cute'
    posts = client.post.find_many(
        where={
            'body': {
                'search': syntax.search_phrase,
            },
        }
    )
    assert len(posts) == 1
    assert 'small and cute' in posts[0].body
