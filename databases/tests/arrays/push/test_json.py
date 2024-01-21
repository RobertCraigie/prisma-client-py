import pytest

from prisma import Json, Prisma


@pytest.mark.asyncio
async def test_pushing_json(client: Prisma) -> None:
    """Pushing a Json[] value"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'json_objects': [Json('foo'), Json(['foo', 'bar'])],
            },
        ),
    ]

    model = await client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'json_objects': {
                'push': [Json.keys(foo='bar'), Json(True)],
            },
        },
    )
    assert model is not None
    assert model.json_objects == [{'foo': 'bar'}, True]

    model = await client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'json_objects': {
                'push': [Json('Baz')],
            },
        },
    )
    assert model is not None
    assert model.json_objects == ['foo', ['foo', 'bar'], 'Baz']
