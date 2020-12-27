import prisma
from prisma import Client


# TODO: actual tests


def test_generation():
    db = Client()
    assert db is not None
    assert db.user is not None
    assert db.post is not None

    assert prisma.client.PostType is not None
    assert prisma.client.UserType is not None
