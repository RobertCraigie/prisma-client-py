import inspect

import pytest
import prisma
from prisma import Prisma


@pytest.mark.asyncio
async def test_base_usage(client: Prisma) -> None:
    """Basic non context manager usage"""
    batcher = client.batch_()
    batcher.user.create({'name': 'Robert'})
    batcher.user.create({'name': 'Tegan'})
    await batcher.commit()

    user = await client.user.find_first(where={'name': 'Robert'})
    assert user is not None
    assert user.name == 'Robert'

    user = await client.user.find_first(where={'name': 'Tegan'})
    assert user is not None
    assert user.name == 'Tegan'


@pytest.mark.asyncio
async def test_context_manager(client: Prisma) -> None:
    """Basic usage with a context manager"""
    async with client.batch_() as batcher:
        batcher.user.create({'name': 'Robert'})
        batcher.user.create({'name': 'Tegan'})

    user = await client.user.find_first(where={'name': 'Robert'})
    assert user is not None
    assert user.name == 'Robert'

    user = await client.user.find_first(where={'name': 'Tegan'})
    assert user is not None
    assert user.name == 'Tegan'


@pytest.mark.asyncio
async def test_batch_error(client: Prisma) -> None:
    """Error while committing does not commit any records"""
    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        batcher = client.batch_()
        batcher.user.create({'id': 'abc', 'name': 'Robert'})
        batcher.user.create({'id': 'abc', 'name': 'Robert 2'})
        await batcher.commit()

    assert exc.match(r'Unique constraint failed on the fields: \(`id`\)')
    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_context_manager_error(client: Prisma) -> None:
    """Error exiting context manager does not commit any records"""
    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        async with client.batch_() as batcher:
            batcher.user.create({'id': 'abc', 'name': 'Robert'})
            batcher.user.create({'id': 'abc', 'name': 'Robert 2'})

    assert exc.match(r'Unique constraint failed on the fields: \(`id`\)')
    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_context_manager_throws_error(client: Prisma) -> None:
    """Context manager respects errors"""
    with pytest.raises(RuntimeError) as exc:
        async with client.batch_() as batcher:
            batcher.user.create({'name': 'Robert'})
            raise RuntimeError('Example error')

    assert exc.match('Example error')
    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_mixing_models(client: Prisma) -> None:
    """Batching queries to multiple models works as intended"""
    async with client.batch_() as batcher:
        # NOTE: this is just to test functionality, the better method
        # for acheiving this is to use nested writes with user.create
        # client.user.create({'name': 'Robert', 'profile': {'create': {'bio': 'Robert\'s profile'}}})
        batcher.user.create({'id': 'abc', 'name': 'Robert'})
        batcher.profile.create(
            {
                'user': {'connect': {'id': 'abc'}},
                'bio': "Robert's profile",
                'country': 'Scotland',
            }
        )

    user = await client.user.find_first(
        where={'name': 'Robert'}, include={'profile': True}
    )
    assert user is not None
    assert user.name == 'Robert'
    assert user.profile is not None
    assert user.profile.bio == "Robert's profile"

    assert await client.user.count() == 1
    assert await client.profile.count() == 1


@pytest.mark.asyncio
async def test_mixing_actions(client: Prisma) -> None:
    """Batching queries to different operations works as intended"""
    async with client.batch_() as batcher:
        batcher.user.create({'name': 'Robert'})
        batcher.user.delete_many(where={'name': 'Robert'})

    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_reusing_batcher(client: Prisma) -> None:
    """Reusing the same batcher does not commit the same query multiple times"""
    batcher = client.batch_()
    batcher.user.create({'name': 'Robert'})
    await batcher.commit()

    assert await client.user.count() == 1

    batcher.user.create({'name': 'Robert 2'})
    await batcher.commit()

    assert await client.user.count() == 2


@pytest.mark.asyncio
async def test_large_query(client: Prisma) -> None:
    """Batching a lot of queries works"""
    async with client.batch_() as batcher:
        for i in range(1000):
            batcher.user.create({'name': f'User {i}'})

    assert await client.user.count() == 1000


@pytest.mark.asyncio
async def test_delete(client: Prisma) -> None:
    """delete action works as suggested"""
    user = await client.user.create({'name': 'Robert'})
    assert await client.user.find_first(where={'id': user.id}) is not None

    async with client.batch_() as batcher:
        batcher.user.delete(where={'id': user.id})

    assert await client.user.find_first(where={'id': user.id}) is None


@pytest.mark.asyncio
async def test_update(client: Prisma) -> None:
    """update action works as suggested"""
    user = await client.user.create({'name': 'Robert'})
    assert await client.user.find_first(where={'id': user.id}) is not None

    async with client.batch_() as batcher:
        batcher.user.update(where={'id': user.id}, data={'name': 'Roberto'})

    new = await client.user.find_first(where={'id': user.id})
    assert new is not None
    assert new.id == user.id
    assert new.name == 'Roberto'


@pytest.mark.asyncio
async def test_upsert(client: Prisma) -> None:
    """upsert action works as suggested"""
    user_id = 'abc123'
    assert await client.user.find_unique(where={'id': user_id}) is None

    async with client.batch_() as batcher:
        batcher.user.upsert(
            where={'id': user_id},
            data={
                'create': {'id': user_id, 'name': 'Robert'},
                'update': {'name': 'Robert'},
            },
        )

    user = await client.user.find_unique(where={'id': user_id})
    assert user is not None
    assert user.id == user_id
    assert user.name == 'Robert'

    async with client.batch_() as batcher:
        batcher.user.upsert(
            where={'id': user_id},
            data={
                'create': {'id': user_id, 'name': 'Robert'},
                'update': {'name': 'Roberto'},
            },
        )

    user = await client.user.find_unique(where={'id': user_id})
    assert user is not None
    assert user.id == user_id
    assert user.name == 'Roberto'
    assert await client.user.count() == 1


@pytest.mark.asyncio
async def test_update_many(client: Prisma) -> None:
    """update_many action works as suggested"""
    await client.user.create({'name': 'Robert'})
    await client.user.create({'name': 'Robert 2'})

    async with client.batch_() as batcher:
        batcher.user.update_many(
            where={'name': {'startswith': 'Robert'}}, data={'name': 'Robert'}
        )

    users = await client.user.find_many()
    assert len(users) == 2
    assert users[0].name == 'Robert'
    assert users[1].name == 'Robert'


@pytest.mark.asyncio
async def test_delete_many(client: Prisma) -> None:
    """delete_many action works as suggested"""
    await client.user.create({'name': 'Robert'})
    await client.user.create({'name': 'Robert 2'})
    assert await client.user.count() == 2

    async with client.batch_() as batcher:
        batcher.user.delete_many(where={'name': {'startswith': 'Robert'}})

    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_create_many_unsupported(client: Prisma) -> None:
    """Cannot call create_many as SQLite does not support it"""
    with pytest.raises(prisma.errors.UnsupportedDatabaseError) as exc:
        async with client.batch_() as batcher:
            batcher.user.create_many([{'name': 'Robert'}])

    assert exc.match(r'create_many\(\) is not supported by sqlite')


def test_ensure_batch_and_action_signatures_are_equal(client: Prisma) -> None:
    """Batch method signature is the same as it's corresponding client method

    This is to ensure that if an client method is updated then it's corresponding
    batch method must also be updated.

    I acknowledge that the presence of this test would normally be considered the
    result of an anti-pattern but I could not figure out any good method for
    implementing batching and client methods together while maintaining static
    type safety and without making the templates horrible to maintain. If you
    have found a method that you think is good please make an issue/PR.
    """
    actions = client.user
    for name, meth in inspect.getmembers(
        client.batch_().user, inspect.ismethod
    ):
        if name.startswith('_'):
            continue

        actual = inspect.signature(meth).replace(
            return_annotation=inspect.Signature.empty
        )
        expected = inspect.signature(getattr(actions, name)).replace(
            return_annotation=inspect.Signature.empty
        )
        assert actual == expected, f'{name} methods are inconsistent'
