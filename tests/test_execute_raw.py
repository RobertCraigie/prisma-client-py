import pytest


@pytest.mark.asyncio
async def test_execute_raw(client):
    post = await client.post.create(
        {
            'title': 'My post title!',
            'published': False,
        }
    )
    assert isinstance(post.id, str)

    query = '''
        UPDATE Post
        SET title = 'My edited title'
        WHERE id = $1
    '''
    count = await client.execute_raw(query, post.id)
    assert count == 1

    found = await client.post.find_unique(where={'id': post.id})
    assert found is not None
    assert found.id == post.id
    assert found.title == 'My edited title'


@pytest.mark.asyncio
async def test_execute_raw_no_result(client):
    query = '''
        UPDATE Post
        SET title = 'updated title'
        WHERE id = 'sdldsd'
    '''
    count = await client.execute_raw(query)
    assert count == 0
