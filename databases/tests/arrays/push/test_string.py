import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_pushing_strings(client: Prisma) -> None:
    """Pushing a String[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'strings': ['a', 'b', 'c'],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'strings': {
                'push': ['a', 'B'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'B']

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'strings': {
                'push': ['d'],
            },
        },
    )
    assert model is not None
    assert model.strings == ['a', 'b', 'c', 'd']
