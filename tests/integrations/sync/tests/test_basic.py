import pytest

from prisma import Prisma, engine


def test_basic(client: Prisma) -> None:
    """Basic call to create, just here as a placeholder, more tests should be added"""
    user = client.user.create({'name': 'Robert'})
    assert user.name == 'Robert'


def test_context_manager() -> None:
    """Client can be used as a context manager to connect and disconnect from the database"""
    client = Prisma()
    assert not client.is_connected()

    with client:
        assert client.is_connected()

    assert not client.is_connected()

    # ensure exceptions are propagated
    with pytest.raises(engine.errors.AlreadyConnectedError):
        with client:
            assert client.is_connected()
            client.connect()
