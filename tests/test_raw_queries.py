import pytest

from prisma import errors, Prisma
from prisma.models import Post, User
from prisma.partials import PostOnlyPublished


@pytest.mark.asyncio
async def test_query_raw(client: Prisma) -> None:
    """Standard usage, erroneous query and correct queries"""
    with pytest.raises(errors.RawQueryError):
        query = """
            SELECT *
            FROM bad_table;
        """
        await client.query_raw(query)

    post = await client.post.create(
        {
            'title': 'My post title!',
            'published': False,
        }
    )

    query = """
        SELECT COUNT(*) as count
        FROM Post
    """
    results = await client.query_raw(query)
    assert len(results) == 1
    assert isinstance(results[0]['count'], int)

    query = """
        SELECT *
        FROM Post
        WHERE id = $1
    """
    results = await client.query_raw(query, post.id)
    assert len(results) == 1
    assert results[0]['id'] == post.id
    assert results[0]['published'] is False


@pytest.mark.asyncio
async def test_query_raw_model(client: Prisma) -> None:
    """Transforms resuls to a BaseModel when given"""
    post = await client.post.create(
        {
            'title': 'My post title!',
            'published': False,
        }
    )

    query = """
        SELECT *
        FROM Post
        WHERE id = $1
    """
    posts = await client.query_raw(query, post.id, model=Post)
    assert len(posts) == 1

    found = posts[0]
    assert isinstance(found, Post)
    assert found == post
    assert found.id == post.id


@pytest.mark.asyncio
async def test_query_raw_partial_model(client: Prisma) -> None:
    """Transforms results to a partial model"""
    posts = [
        await client.post.create({'title': 'foo', 'published': False}),
        await client.post.create({'title': 'foo', 'published': True}),
        await client.post.create({'title': 'foo', 'published': True}),
        await client.post.create({'title': 'foo', 'published': False}),
    ]
    query = """
        SELECT id, published
        FROM Post
        WHERE published = 0
    """
    results = await client.query_raw(query, model=PostOnlyPublished)
    assert len(results) == 2
    assert {p.id for p in results} == {
        p.id for p in posts if p.published is False
    }
    assert not hasattr(results[0], 'title')
    assert results[0].published is False
    assert results[1].published is False


@pytest.mark.asyncio
async def test_query_raw_no_result(client: Prisma) -> None:
    """No result returns empty list"""
    query = """
        SELECT *
        FROM Post
        WHERE id = 'sdldsd'
    """
    results = await client.query_raw(query)
    assert len(results) == 0

    results = await client.query_raw(query, model=Post)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_query_raw_incorrect_params(client: Prisma) -> None:
    """Passings too many parameters raises an error"""
    query = """
        SELECT COUNT(*) as total
        FROM Post
    """
    results = await client.query_raw(query)
    assert len(results) == 1
    assert results[0]['total'] == 0

    with pytest.raises(errors.RawQueryError):
        await client.query_raw(query, 1)


@pytest.mark.asyncio
async def test_execute_raw(client: Prisma) -> None:
    """Basic usage"""
    post = await client.post.create(
        {
            'title': 'My post title.',
            'published': False,
        }
    )
    assert isinstance(post.id, str)

    query = """
        UPDATE Post
        SET title = 'My edited title'
        WHERE id = $1
    """
    count = await client.execute_raw(query, post.id)
    assert count == 1

    found = await client.post.find_unique(where={'id': post.id})
    assert found is not None
    assert found.id == post.id
    assert found.title == 'My edited title'


@pytest.mark.asyncio
async def test_execute_raw_no_result(client: Prisma) -> None:
    """No result returns 0"""
    query = """
        UPDATE Post
        SET title = 'updated title'
        WHERE id = 'sdldsd'
    """
    count = await client.execute_raw(query)
    assert count == 0


@pytest.mark.asyncio
async def test_query_first(client: Prisma) -> None:
    """Standard usage"""
    user = await client.user.create({'name': 'Robert'})

    query = """
        SELECT *
        FROM User
        WHERE User.id = ?
    """
    found = await client.query_first(query, user.id)
    found.pop('created_at')
    assert found == {'id': user.id, 'name': 'Robert', 'email': None}


@pytest.mark.asyncio
async def test_query_first_model(client: Prisma) -> None:
    """Transforms result to a BaseModel if given"""
    user = await client.user.create({'name': 'Robert'})

    query = """
        SELECT *
        FROM User
        WHERE User.id = ?
    """
    found = await client.query_first(query, user.id, model=User)
    assert found is not None
    assert found.id == user.id
    assert found.name == 'Robert'
