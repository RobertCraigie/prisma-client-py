import inspect

import pytest
import prisma
from prisma import Client


@pytest.mark.asyncio
async def test_base_usage(client: Client) -> None:
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
async def test_context_manager(client: Client) -> None:
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
async def test_batch_error(client: Client) -> None:
    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        batcher = client.batch_()
        batcher.user.create({'id': 'abc', 'name': 'Robert'})
        batcher.user.create({'id': 'abc', 'name': 'Robert 2'})
        await batcher.commit()

    assert exc.match(r'Unique constraint failed on the fields: \(`id`\)')
    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_context_manager_error(client: Client) -> None:
    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        async with client.batch_() as batcher:
            batcher.user.create({'id': 'abc', 'name': 'Robert'})
            batcher.user.create({'id': 'abc', 'name': 'Robert 2'})

    assert exc.match(r'Unique constraint failed on the fields: \(`id`\)')
    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_context_manager_throws_error(client: Client) -> None:
    with pytest.raises(RuntimeError) as exc:
        async with client.batch_() as batcher:
            batcher.user.create({'name': 'Robert'})
            raise RuntimeError('Example error')

    assert exc.match('Example error')
    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_mixing_models(client: Client) -> None:
    async with client.batch_() as batcher:
        # NOTE: this is just to test functionality, the better method
        # for acheiving this is to use nested writes with user.create
        # client.user.create({'name': 'Robert', 'profile': {'create': {'bio': 'Robert\'s profile'}}})
        batcher.user.create({'id': 'abc', 'name': 'Robert'})
        batcher.profile.create(
            {'user': {'connect': {'id': 'abc'}}, 'bio': 'Robert\'s profile'}
        )

    user = await client.user.find_first(
        where={'name': 'Robert'}, include={'profile': True}
    )
    assert user is not None
    assert user.name == 'Robert'
    assert user.profile is not None
    assert user.profile.bio == 'Robert\'s profile'

    assert await client.user.count() == 1
    assert await client.profile.count() == 1


@pytest.mark.asyncio
async def test_mixing_actions(client: Client) -> None:
    async with client.batch_() as batcher:
        batcher.user.create({'name': 'Robert'})
        batcher.user.delete_many(where={'name': 'Robert'})

    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_reusing_batcher(client: Client) -> None:
    batcher = client.batch_()
    batcher.user.create({'name': 'Robert'})
    await batcher.commit()

    assert await client.user.count() == 1

    batcher.user.create({'name': 'Robert 2'})
    await batcher.commit()

    assert await client.user.count() == 2


@pytest.mark.asyncio
async def test_large_query(client: Client) -> None:
    async with client.batch_() as batcher:
        for i in range(1000):
            batcher.user.create({'name': f'User {i}'})

    assert await client.user.count() == 1000


@pytest.mark.asyncio
async def test_delete(client: Client) -> None:
    user = await client.user.create({'name': 'Robert'})
    assert await client.user.find_first(where={'id': user.id}) is not None

    async with client.batch_() as batcher:
        batcher.user.delete(where={'id': user.id})

    assert await client.user.find_first(where={'id': user.id}) is None


@pytest.mark.asyncio
async def test_update(client: Client) -> None:
    user = await client.user.create({'name': 'Robert'})
    assert await client.user.find_first(where={'id': user.id}) is not None

    async with client.batch_() as batcher:
        batcher.user.update(where={'id': user.id}, data={'name': 'Roberto'})

    new = await client.user.find_first(where={'id': user.id})
    assert new is not None
    assert new.id == user.id
    assert new.name == 'Roberto'


@pytest.mark.asyncio
async def test_upsert(client: Client) -> None:
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
async def test_update_many(client: Client) -> None:
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
async def test_delete_many(client: Client) -> None:
    await client.user.create({'name': 'Robert'})
    await client.user.create({'name': 'Robert 2'})
    assert await client.user.count() == 2

    async with client.batch_() as batcher:
        batcher.user.delete_many(where={'name': {'startswith': 'Robert'}})

    assert await client.user.count() == 0


@pytest.mark.asyncio
async def test_create_many_unsupported(client: Client) -> None:
    with pytest.raises(prisma.errors.UnsupportedDatabaseError) as exc:
        async with client.batch_() as batcher:
            batcher.user.create_many([{'name': 'Robert'}])

    assert exc.match(r'create_many\(\) is not supported by sqlite')


def test_ensure_batch_and_action_signatures_are_equal(client: Client) -> None:
    # ensure tests will fail if an action method is updated without
    # updating the corresponding batch method
    actions = client.user
    for name, meth in inspect.getmembers(client.batch_().user, inspect.ismethod):
        if name.startswith('_'):
            continue

        actual = inspect.signature(meth).replace(
            return_annotation=inspect.Signature.empty
        )
        expected = inspect.signature(getattr(actions, name)).replace(
            return_annotation=inspect.Signature.empty
        )
        assert actual == expected, f'{name} methods are inconsistent'
