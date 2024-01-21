import pytest

import prisma
from prisma import Prisma, register, get_client
from prisma.testing import reset_client, unregister_client


@pytest.mark.prisma
def test_reset_client() -> None:
    """Resetting and re-registering the registered client works as expected"""
    original = get_client()
    assert isinstance(original, Prisma)

    # ensure the test is sound
    assert Prisma() != original

    with pytest.raises(prisma.errors.ClientAlreadyRegisteredError):
        register(Prisma())

    with reset_client():
        with pytest.raises(prisma.errors.ClientNotRegisteredError):
            get_client()

        with pytest.raises(prisma.errors.ClientNotRegisteredError):
            with reset_client():
                ...

        client = Prisma()
        register(client)
        assert get_client() == client

    assert get_client() == original


@pytest.mark.prisma
def test_unregister_client() -> None:
    """Unregistering the client works as expected"""
    original = get_client()
    assert isinstance(original, Prisma)
    unregister_client()

    with pytest.raises(prisma.errors.ClientNotRegisteredError):
        get_client()

    with pytest.raises(prisma.errors.ClientNotRegisteredError):
        unregister_client()

    # test cleanup
    register(original)
