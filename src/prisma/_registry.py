from __future__ import annotations

from typing import TYPE_CHECKING, Union, Callable

from .errors import ClientNotRegisteredError, ClientAlreadyRegisteredError

if TYPE_CHECKING:
    from .client import Prisma  # noqa: TID251


RegisteredClient = Union['Prisma', Callable[[], 'Prisma']]
_registered_client: RegisteredClient | None = None


def register(client: RegisteredClient) -> None:
    """Register a client instance to be retrieved by `get_client()`

    This function _must_ only be called once, preferrably as soon as possible
    to avoid any potentially confusing errors with threads or processes.
    """
    from .client import Prisma  # noqa: TID251

    global _registered_client

    if _registered_client is not None:
        raise ClientAlreadyRegisteredError()

    if not isinstance(client, Prisma) and not callable(client):
        raise TypeError(
            f'Expected either a {Prisma} instance or a function that returns a {Prisma} but got {client} instead.'
        )

    _registered_client = client


def get_client() -> Prisma:
    """Get the registered client instance

    Raises errors.ClientNotRegisteredError() if no client instance has been registered.
    """
    from .client import Prisma  # noqa: TID251

    registered = _registered_client
    if registered is None:
        raise ClientNotRegisteredError() from None

    if isinstance(registered, Prisma):
        return registered

    client = registered()
    if not isinstance(client, Prisma):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError(f'Registered function returned {client} instead of a {Prisma} instance.')

    return client
