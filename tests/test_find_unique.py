import pytest
from pydantic import ValidationError

from prisma import errors


@pytest.mark.asyncio
async def test_find_unique(client):
    post = await client.post.create(
        {
            'title': 'My post title!',
            'published': False,
        }
    )
    assert isinstance(post.id, str)

    found = await client.post.find_unique(where={'id': post.id})
    assert found is not None
    assert found == post


@pytest.mark.asyncio
async def test_find_unique_missing_required_args(client):
    with pytest.raises(ValidationError):
        await client.post.find_unique()

    # TODO: more constrained error type
    with pytest.raises(errors.DataError):
        await client.post.find_unique(
            {
                'title': 'Hi from Prisma!',
            }
        )


@pytest.mark.asyncio
async def test_find_unique_no_match(client):
    found = await client.post.find_unique(where={'id': 'sjbsjahs'})
    assert found is None
