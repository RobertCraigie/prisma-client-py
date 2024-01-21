import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_pushing_floats(client: Prisma) -> None:
    """Pushing a Float[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'floats': [3.4, 6.8, 12.4],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'floats': {
                'push': [102.3, 500.7],
            },
        },
    )
    assert model is not None
    assert model.floats == [102.3, 500.7]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'floats': {
                'push': [20],
            },
        },
    )
    assert model is not None
    assert model.floats == [3.4, 6.8, 12.4, 20]
