import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_pushing_bigints(client: Prisma) -> None:
    """Pushing values to a BigInt[] field"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'bigints': [539506179039297536, 281454500584095754],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'bigints': {
                'push': [538075535121842179],
            },
        },
    )
    assert model is not None
    assert model.bigints == [538075535121842179]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bigints': {
                'push': [186214420957888512],
            },
        },
    )
    assert model is not None
    assert model.bigints == [
        539506179039297536,
        281454500584095754,
        186214420957888512,
    ]
