import pytest
from prisma import Prisma, errors


@pytest.mark.asyncio
async def test_find_unique_id_field(client: Prisma) -> None:
    """Finding a record by an ID field"""
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
async def test_find_unique_missing_required_args(client: Prisma) -> None:
    """Missing field raises an error"""
    with pytest.raises(TypeError):
        await client.post.find_unique()  # type: ignore[call-arg]

    # TODO: more constrained error type
    with pytest.raises(errors.DataError):
        await client.post.find_unique(
            {
                'title': 'Hi from Prisma!',  # pyright: ignore
            }
        )


@pytest.mark.asyncio
async def test_find_unique_no_match(client: Prisma) -> None:
    """Looking for non-existent record does not error"""
    found = await client.post.find_unique(where={'id': 'sjbsjahs'})
    assert found is None


@pytest.mark.asyncio
async def test_multiple_fields_are_not_allowed(client: Prisma) -> None:
    """Multiple fields cannot be passed at once"""
    with pytest.raises(errors.DataError):
        await client.user.find_unique(
            where={
                'id': 'foo',
                'email': 'foo',  # type: ignore
            },
        )
