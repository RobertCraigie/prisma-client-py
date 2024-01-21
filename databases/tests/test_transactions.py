import asyncio
from typing import Optional
from datetime import timedelta

import pytest

import prisma
from prisma import Prisma
from prisma.models import User, Profile

from ..utils import CURRENT_DATABASE


@pytest.mark.asyncio
async def test_model_query(client: Prisma) -> None:
    """Basic usage within model queries"""
    async with client.tx(timeout=timedelta(milliseconds=1000)) as tx:
        user = await User.prisma(tx).create({'name': 'Robert'})
        assert user.name == 'Robert'

        # ensure not commited outside transaction
        assert await client.user.count() == 0

        await Profile.prisma(tx).create(
            {
                'description': 'Hello, there!',
                'country': 'Scotland',
                'user': {
                    'connect': {
                        'id': user.id,
                    },
                },
            },
        )

    found = await client.user.find_unique(where={'id': user.id}, include={'profile': True})
    assert found is not None
    assert found.name == 'Robert'
    assert found.profile is not None
    assert found.profile.description == 'Hello, there!'


@pytest.mark.asyncio
async def test_context_manager(client: Prisma) -> None:
    """Basic usage within a context manager"""
    async with client.tx(timeout=timedelta(milliseconds=1000)) as transaction:
        user = await transaction.user.create({'name': 'Robert'})
        assert user.name == 'Robert'

        # ensure not commited outside transaction
        assert await client.user.count() == 0

        await transaction.profile.create(
            {
                'description': 'Hello, there!',
                'country': 'Scotland',
                'user': {
                    'connect': {
                        'id': user.id,
                    },
                },
            },
        )

    found = await client.user.find_unique(where={'id': user.id}, include={'profile': True})
    assert found is not None
    assert found.name == 'Robert'
    assert found.profile is not None
    assert found.profile.description == 'Hello, there!'


@pytest.mark.asyncio
async def test_context_manager_auto_rollback(client: Prisma) -> None:
    """An error being thrown when within a context manager causes the transaction to be rolled back"""
    user: Optional[User] = None

    with pytest.raises(RuntimeError) as exc:
        async with client.tx() as tx:
            user = await tx.user.create({'name': 'Tegan'})
            raise RuntimeError('Error ocurred mid transaction.')

    assert exc.match('Error ocurred mid transaction.')

    assert user is not None
    found = await client.user.find_unique(where={'id': user.id})
    assert found is None


@pytest.mark.asyncio
async def test_batch_within_transaction(client: Prisma) -> None:
    """Query batching can be used within transactions"""
    async with client.tx(timeout=timedelta(milliseconds=10000)) as transaction:
        async with transaction.batch_() as batcher:
            batcher.user.create({'name': 'Tegan'})
            batcher.user.create({'name': 'Robert'})

        assert await client.user.count() == 0
        assert await transaction.user.count() == 2

    assert await client.user.count() == 2


@pytest.mark.asyncio
async def test_timeout(client: Prisma) -> None:
    """A `TransactionExpiredError` is raised when the transaction times out."""
    # this outer block is necessary becuse to the context manager it appears that no error
    # ocurred so it will attempt to commit the transaction, triggering the expired error again
    with pytest.raises(prisma.errors.TransactionExpiredError):
        async with client.tx(timeout=timedelta(milliseconds=50)) as transaction:
            await asyncio.sleep(0.05)

            with pytest.raises(prisma.errors.TransactionExpiredError) as exc:
                await transaction.user.create({'name': 'Robert'})

            raise exc.value


@pytest.mark.asyncio
@pytest.mark.skipif(CURRENT_DATABASE == 'sqlite', reason='This is currently broken...')
async def test_concurrent_transactions(client: Prisma) -> None:
    """Two separate transactions can be used independently of each other at the same time"""
    timeout = timedelta(milliseconds=15000)
    async with client.tx(timeout=timeout) as tx1, client.tx(timeout=timeout) as tx2:
        user1 = await tx1.user.create({'name': 'Tegan'})
        user2 = await tx2.user.create({'name': 'Robert'})

        assert await tx1.user.find_first(where={'name': 'Robert'}) is None
        assert await tx2.user.find_first(where={'name': 'Tegan'}) is None

        found = await tx1.user.find_first(where={'name': 'Tegan'})
        assert found is not None
        assert found.id == user1.id

        found = await tx2.user.find_first(where={'name': 'Robert'})
        assert found is not None
        assert found.id == user2.id

        # ensure not leaked
        assert await client.user.count() == 0
        assert (await tx1.user.find_first(where={'name': user2.name})) is None
        assert (await tx2.user.find_first(where={'name': user1.name})) is None

    assert await client.user.count() == 2


@pytest.mark.asyncio
async def test_transaction_raises_original_error(client: Prisma) -> None:
    """If an error is raised during the execution of the transaction, it is raised"""
    with pytest.raises(RuntimeError, match=r'Test error!'):
        async with client.tx():
            raise RuntimeError('Test error!')


@pytest.mark.asyncio
async def test_transaction_within_transaction_warning(client: Prisma) -> None:
    """A warning is raised if a transaction is started from another transaction client"""
    tx1 = await client.tx().start()
    with pytest.warns(UserWarning) as warnings:
        await tx1.tx().start()

    assert len(warnings) == 1
    record = warnings[0]
    assert not isinstance(record.message, str)
    assert (
        record.message.args[0]
        == 'The current client is already in a transaction. This can lead to surprising behaviour.'
    )
    assert record.filename == __file__


@pytest.mark.asyncio
async def test_transaction_within_transaction_context_warning(
    client: Prisma,
) -> None:
    """A warning is raised if a transaction is started from another transaction client"""
    async with client.tx() as tx1:
        with pytest.warns(UserWarning) as warnings:
            async with tx1.tx():
                pass

    assert len(warnings) == 1
    record = warnings[0]
    assert not isinstance(record.message, str)
    assert (
        record.message.args[0]
        == 'The current client is already in a transaction. This can lead to surprising behaviour.'
    )
    assert record.filename == __file__


@pytest.mark.asyncio
async def test_transaction_not_started(client: Prisma) -> None:
    """A `TransactionNotStartedError` is raised when attempting to call `commit()` or `rollback()`
    on a transaction that hasn't been started yet.
    """
    tx = client.tx()

    with pytest.raises(prisma.errors.TransactionNotStartedError):
        await tx.commit()

    with pytest.raises(prisma.errors.TransactionNotStartedError):
        await tx.rollback()


@pytest.mark.asyncio
async def test_transaction_already_closed(client: Prisma) -> None:
    """Attempting to use a transaction outside of the context block raises an error"""
    async with client.tx() as transaction:
        pass

    with pytest.raises(prisma.errors.TransactionExpiredError) as exc:
        await transaction.user.delete_many()

    assert exc.match('Transaction already closed')
