import threading
from typing import Optional, Any

from prisma import Client
from prisma.models import User


class PropagatingThread(threading.Thread):
    """
    Wrapper around `threading.Thread` that propagates exceptions.

    REF: https://gist.github.com/sbrugman/59b3535ebcd5aa0e2598293cfa58b6ab
    """

    exc: Optional[BaseException]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.exc = None

    def run(self) -> None:
        try:
            super().run()
        except BaseException as e:
            self.exc = e

    def join(self, timeout: int = None) -> None:
        super().join(timeout)
        if self.exc is not None:
            raise self.exc


def test_create() -> None:
    """Creating a user model using model-based access"""
    user = User.prisma().create({'name': 'Robert'})
    assert isinstance(user, User)
    assert user.name == 'Robert'


def test_threading(client: Client) -> None:
    """Ensure the registered client is shared between threads"""

    def runner() -> None:
        user = User.prisma().create({'name': 'Robert'})
        assert user.name == 'Robert'

    thread = PropagatingThread(target=runner)
    thread.start()
    thread.join()
