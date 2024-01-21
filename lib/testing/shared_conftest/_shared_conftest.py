import asyncio
from typing import TYPE_CHECKING, Iterable, Iterator
from pathlib import Path

import pytest

from prisma.utils import get_or_create_event_loop
from prisma.testing import reset_client

from ._utils import request_has_client

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch


__all__ = (
    'setup_env',
    'event_loop',
    'patch_prisma_fixture',
)

HOME_DIR = Path.home()


@pytest.fixture(scope='session')
def event_loop() -> Iterable[asyncio.AbstractEventLoop]:
    loop = get_or_create_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: 'MonkeyPatch') -> None:
    # Set a custom home directory to use for caching binaries so that
    # when we make use of pytest's temporary directory functionality the binaries
    # don't have to be downloaded again.
    monkeypatch.setenv('PRISMA_HOME_DIR', str(HOME_DIR))


@pytest.fixture(name='patch_prisma', autouse=True)
def patch_prisma_fixture(request: 'FixtureRequest') -> Iterator[None]:
    if request_has_client(request):
        yield
    else:

        def _disable_access() -> None:
            raise RuntimeError(  # pragma: no cover
                'Tests that access the prisma client must be decorated with: ' '@pytest.mark.prisma'
            )

        with reset_client(_disable_access):  # type: ignore
            yield
