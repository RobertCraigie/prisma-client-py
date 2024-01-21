import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_delete(client: Prisma) -> None:
    """Deleting a record with a relationship does not delete the related record"""
    post = await client.post.create(
        {
            'title': 'Hi from Prisma!',
            'published': False,
            'author': {'create': {'name': 'Alice'}},
        },
        include={'author': True},
    )
    assert post.title == 'Hi from Prisma!'
    assert post.author is not None
    assert post.author.name == 'Alice'

    deleted = await client.post.delete(where={'id': post.id}, include={'author': True})
    assert deleted is not None
    assert deleted.title == 'Hi from Prisma!'
    assert deleted.author is not None
    assert deleted.author.name == 'Alice'

    found = await client.post.find_unique(where={'id': post.id}, include={'author': True})
    assert found is None

    user = await client.user.find_unique(where={'id': post.author.id})
    assert user is not None
    assert user.name == 'Alice'


@pytest.mark.asyncio
async def test_delete_record_not_found(client: Prisma) -> None:
    """Deleting a non-existent record returns None"""
    deleted = await client.post.delete(where={'id': 'ksdjsdh'})
    assert deleted is None
