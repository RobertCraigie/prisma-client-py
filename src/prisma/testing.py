import contextlib
from typing import Iterator

from . import client as _client
from .errors import ClientNotRegisteredError


@contextlib.contextmanager
def reset_client() -> Iterator[None]:
    """Context manager to unregister the current client

    Once the context manager exits, the registered client is set back to it's original state
    """
    # pylint: disable=protected-access
    client = _client._registered_client
    if client is None:
        raise ClientNotRegisteredError()

    try:
        _client._registered_client = None
        yield
    finally:
        _client._registered_client = client
