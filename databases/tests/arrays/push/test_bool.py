import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_pushing_boolean(client: Prisma) -> None:
    """Pushing values to a Boolean[] field"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'bools': [False, True],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'bools': {
                'push': [True, False, True],
            },
        },
    )
    assert model is not None
    assert model.bools == [True, False, True]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bools': {
                'push': [False],
            },
        },
    )
    assert model is not None
    assert model.bools == [False, True, False]
