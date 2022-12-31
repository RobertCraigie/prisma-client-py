from decimal import Decimal

import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_pushing_decimal(client: Prisma) -> None:
    """Pushing a Decimal[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'decimals': [Decimal('22.99'), Decimal('30.01')],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'decimals': {
                'push': [Decimal('22.99'), Decimal('31')],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal('22.99'), Decimal('31')]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'decimals': {
                'push': [Decimal('5')],
            },
        },
    )
    assert model is not None
    assert model.decimals == [Decimal('22.99'), Decimal('30.01'), Decimal('5')]
