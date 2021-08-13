import pytest

from prisma import errors, Client


@pytest.mark.asyncio
async def test_find_unique(client: Client) -> None:
    """Standard usage"""
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
async def test_find_unique_missing_required_args(client: Client) -> None:
    """Missing field raises an error"""
    with pytest.raises(TypeError):
        await client.post.find_unique()  # type: ignore[call-arg]

    # TODO: more constrained error type
    with pytest.raises(errors.DataError):
        await client.post.find_unique(
            {  # type: ignore[typeddict-item]
                'title': 'Hi from Prisma!',
            }
        )


@pytest.mark.asyncio
async def test_find_unique_no_match(client: Client) -> None:
    """Looking for non-existent record does not error"""
    found = await client.post.find_unique(where={'id': 'sjbsjahs'})
    assert found is None
