import pytest

from prisma import errors, Client
from prisma.models import Post


@pytest.mark.asyncio
async def test_query_raw(client: Client) -> None:
    with pytest.raises(errors.RawQueryError):
        query = '''
            SELECT *
            FROM bad_table;
        '''
        await client.query_raw(query)

    post = await client.post.create(
        {
            'title': 'My post title!',
            'published': False,
        }
    )

    query = '''
        SELECT COUNT(*) as count
        FROM Post
    '''
    results = await client.query_raw(query)
    assert len(results) == 1
    assert isinstance(results[0]['count'], int)

    query = '''
        SELECT *
        FROM Post
        WHERE id = $1
    '''
    results = await client.query_raw(query, post.id)
    assert len(results) == 1
    assert results[0]['id'] == post.id
    assert results[0]['published'] is False


@pytest.mark.asyncio
async def test_query_raw_model(client: Client) -> None:
    post = await client.post.create(
        {
            'title': 'My post title!',
            'published': False,
        }
    )

    query = '''
        SELECT *
        FROM Post
        WHERE id = $1
    '''
    posts = await client.query_raw(query, post.id, model=Post)
    assert len(posts) == 1

    found = posts[0]
    assert isinstance(found, Post)
    assert found == post
    assert found.id == post.id


@pytest.mark.asyncio
async def test_query_raw_no_result(client: Client) -> None:
    query = '''
        SELECT *
        FROM Post
        WHERE id = 'sdldsd'
    '''
    results = await client.query_raw(query)
    assert len(results) == 0

    results = await client.query_raw(query, model=Post)
    assert len(results) == 0


@pytest.mark.asyncio
@pytest.mark.skip(reason='This is an internal prisma query engine bug')
async def test_query_raw_incorrect_params(client: Client) -> None:
    query = '''
        SELECT COUNT(*)
        FROM Post
    '''
    await client.query_raw(query, 1)
