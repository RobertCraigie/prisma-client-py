from __future__ import annotations

import contextlib
from typing import Iterator

from . import _registry
from .errors import ClientNotRegisteredError
from ._registry import RegisteredClient


@contextlib.contextmanager
def reset_client(
    new_client: RegisteredClient | None = None,
) -> Iterator[None]:
    """Context manager to unregister the current client

    Once the context manager exits, the registered client is set back to it's original state
    """
    client = _registry._registered_client
    if client is None:
        raise ClientNotRegisteredError()

    try:
        _registry._registered_client = new_client
        yield
    finally:
        _registry._registered_client = client


def unregister_client() -> None:
    """Unregister the current client."""
    if _registry._registered_client is None:
        raise ClientNotRegisteredError()

    _registry._registered_client = None
