import prisma


def test_generation():
    client = prisma.Client()
    assert client is not None
