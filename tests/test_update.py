import pytest
from prisma import Client


@pytest.fixture(scope='module', name='user_id')
async def user_id_fixture(client: Client) -> str:
    user = await client.user.create({'name': 'Robert'})
    return user.id


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_update(client: Client) -> None:
    post = await client.post.create(
        {
            'title': 'Hi from Create!',
            'published': True,
            'desc': 'Prisma is a database toolkit that makes databases easy.',
            'author': {'create': {'name': 'Bob'}},
        }
    )
    assert post.author is None
    assert post.title == 'Hi from Create!'
    updated = await client.post.update(
        where={'id': post.id}, data={'title': 'Hi from Update!'}
    )
    assert updated is not None
    assert updated.title == 'Hi from Update!'
    assert updated.updated_at != post.updated_at
    assert updated.created_at == post.created_at

    updated = await client.post.update(
        where={'id': post.id},
        include={'author': True},
        data={'published': {'set': False}, 'desc': 'Updated desc.'},
    )
    assert updated is not None
    assert updated.published is False
    assert updated.desc == 'Updated desc.'
    assert updated.author is not None
    assert updated.author.name == 'Bob'


@pytest.mark.asyncio
@pytest.mark.persist_data
@pytest.mark.parametrize('method', ['disconnect', 'delete'])
async def test_update_with_create_disconnect(
    client: Client, user_id: str, method: str
) -> None:
    user = await client.user.find_unique(where={'id': user_id}, include={'posts': True})
    assert user is not None
    assert len(user.posts) == 0

    updated = await client.user.update(
        where={'id': user_id},
        data={'posts': {'create': [{'title': 'My post', 'published': True}]}},
        include={'posts': True},
    )
    assert updated is not None
    assert len(updated.posts) == 1

    if method == 'disconnect':
        updated = await client.user.update(
            where={'id': user_id},
            data={'posts': {'disconnect': [{'id': updated.posts[0].id}]}},
            include={'posts': True},
        )
    else:
        updated = await client.user.update(
            where={'id': user_id},
            data={'posts': {'delete': [{'id': updated.posts[0].id}]}},
            include={'posts': True},
        )

    assert updated is not None
    assert len(updated.posts) == 0


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_atomic_update(client: Client) -> None:
    post = await client.post.create({'title': 'My Post', 'published': False})
    assert post.title == 'My Post'
    assert post.views == 0

    updated = await client.post.update(
        where={'id': post.id}, data={'views': {'increment': 1}}
    )
    assert updated is not None
    assert updated.views == 1


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_update_record_not_found(client: Client) -> None:
    post = await client.post.update(
        where={'id': 'wow'}, data={'title': 'Hi from Update!'}
    )
    assert post is None
