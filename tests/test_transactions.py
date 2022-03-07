import asyncio
from typing import Optional

import pytest

import prisma
from prisma import Prisma
from prisma.models import User


# TODO: more tests


@pytest.mark.asyncio
async def test_context_manager(client: Prisma) -> None:
    async with client.tx() as transaction:
        user = await transaction.user.create({'name': 'Robert'})
        assert user.name == 'Robert'

        # ensure not commited outside transaction
        assert await client.user.count() == 0

        await transaction.profile.create(
            {
                'bio': 'Hello, there!',
                'country': 'Scotland',
                'user': {
                    'connect': {
                        'id': user.id,
                    },
                },
            },
        )

    found = await client.user.find_unique(
        where={'id': user.id}, include={'profile': True}
    )
    assert found is not None
    assert found.name == 'Robert'
    assert found.profile is not None
    assert found.profile.bio == 'Hello, there!'


@pytest.mark.asyncio
async def test_context_manager_auto_rollback(client: Prisma) -> None:
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
    async with client.tx(timeout=6000) as transaction:
        async with transaction.batch_() as batcher:
            batcher.user.create({'name': 'Tegan'})
            batcher.user.create({'name': 'Robert'})

        assert await client.user.count() == 0
        assert await transaction.user.count() == 2

    assert await client.user.count() == 2


@pytest.mark.asyncio
async def test_timeout(client: Prisma) -> None:
    async with client.tx(timeout=50) as transaction:
        await asyncio.sleep(0.05)

        with pytest.raises(prisma.errors.TransactionExpiredError):
            await transaction.user.create({'name': 'Robert'})


@pytest.mark.asyncio
async def test_concurrent_transactions(client: Prisma) -> None:
    timeout = 10000
    async with client.tx(timeout=timeout) as tx1, client.tx(
        timeout=timeout
    ) as tx2:
        user1 = await tx1.user.create({'name': 'Tegan'})
        user2 = await tx2.user.create({'name': 'Robert'})

        assert await tx1.user.find_first(where={'name': 'Robert'}) is None
        assert await tx2.user.find_first(where={'name': 'Tegan'}) is None

        assert (
            await tx1.user.find_first(where={'name': 'Tegan'}).id == user1.id
        )
        assert (
            await tx2.user.find_first(where={'name': 'Robert'}).id == user2.id
        )

    assert await client.user.count() == 2


@pytest.mark.asyncio
async def test_transaction_within_transaction_warning(client: Prisma) -> None:
    tx1 = await client.tx().start()
    with pytest.warns(UserWarning) as warnings:
        await tx1.tx().start()

    assert len(warnings) == 1
    record = warnings[0]
    assert not isinstance(record.message, str)
    assert (
        record.message.args[0]
        == 'The current client is already in a transaction.'
    )
    assert record.filename == __file__


@pytest.mark.asyncio
async def test_transaction_within_transaction_context_warning(
    client: Prisma,
) -> None:
    async with client.tx() as tx1:
        with pytest.warns(UserWarning) as warnings:
            async with tx1.tx():
                pass

    assert len(warnings) == 1
    record = warnings[0]
    assert not isinstance(record.message, str)
    assert (
        record.message.args[0]
        == 'The current client is already in a transaction.'
    )
    assert record.filename == __file__


@pytest.mark.asyncio
async def test_transaction_not_started(client: Prisma) -> None:
    tx = client.tx()

    with pytest.raises(prisma.errors.TransactionNotStartedError):
        await tx.commit()

    with pytest.raises(prisma.errors.TransactionNotStartedError):
        await tx.rollback()


@pytest.mark.asyncio
async def test_transaction_already_closed(client: Prisma) -> None:
    async with client.tx() as transaction:
        pass

    with pytest.raises(prisma.errors.TransactionError) as exc:
        await transaction.user.delete_many()

    assert exc.match(
        'Transaction API error: Transaction already closed: '
        "Transaction is no longer valid. Last state: 'Committed'"
    )
