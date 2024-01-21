from prisma import Base64, Prisma


def test_pushing_byte(client: Prisma) -> None:
    """Pushing values to a Bytes[] field"""
    models = [
        client.lists.create({}),
        client.lists.create(
            data={
                'bytes': [Base64.encode(b'foo'), Base64.encode(b'bar')],
            },
        ),
    ]

    model = client.lists.update(
        where={
            'id': models[0].id,
        },
        data={
            'bytes': {
                'push': [Base64.encode(b'a'), Base64.encode(b'b')],
            },
        },
    )
    assert model is not None
    assert model.bytes == [Base64.encode(b'a'), Base64.encode(b'b')]

    model = client.lists.update(
        where={
            'id': models[1].id,
        },
        data={
            'bytes': {
                'push': [Base64.encode(b'baz')],
            },
        },
    )
    assert model is not None
    assert model.bytes == [
        Base64.encode(b'foo'),
        Base64.encode(b'bar'),
        Base64.encode(b'baz'),
    ]
