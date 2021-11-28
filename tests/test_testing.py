import pytest
import prisma
from prisma import Client, register, get_client
from prisma.testing import reset_client


def test_reset_client() -> None:
    """Resetting and re-registering the registered client works as expected"""
    original = get_client()
    assert isinstance(original, Client)

    # ensure the test is sound
    assert Client() != original

    with pytest.raises(prisma.errors.ClientAlreadyRegisteredError):
        register(Client())

    with reset_client():
        with pytest.raises(prisma.errors.ClientNotRegisteredError):
            get_client()

        with pytest.raises(prisma.errors.ClientNotRegisteredError):
            with reset_client():
                ...

        client = Client()
        register(client)
        assert get_client() == client

    assert get_client() == original
