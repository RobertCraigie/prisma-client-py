# pylint: disable=global-statement
import os
import sys
import asyncio
from typing import List, Iterator, TYPE_CHECKING

import pytest

from prisma import Client
from prisma.cli import setup_logging

from . import contexts
from .utils import Runner, Testdir


if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.monkeypatch import MonkeyPatch
    from _pytest.pytester import Testdir as PytestTestdir


pytest_plugins = ['pytester']
LOGGING_CONTEXT_MANAGER = setup_logging(use_handler=False)


@pytest.fixture(name='client')
def client_fixture(prisma: Client) -> Client:
    return prisma


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.fixture()
def runner(monkeypatch: 'MonkeyPatch') -> Runner:
    """Fixture for running cli tests"""
    return Runner(patcher=monkeypatch)


@pytest.fixture(name='testdir')
def testdir_fixture(testdir: 'PytestTestdir') -> Iterator[Testdir]:
    cwd = os.getcwd()
    os.chdir(testdir.tmpdir)
    sys.path.insert(0, str(testdir.tmpdir))

    yield Testdir(testdir)

    os.chdir(cwd)
    sys.path.remove(str(testdir.tmpdir))


# TODO: don't emulate the with statement
def pytest_sessionstart(session: pytest.Session) -> None:
    LOGGING_CONTEXT_MANAGER.__enter__()  # pylint: disable=no-member


def pytest_sessionfinish(session: pytest.Session) -> None:
    if LOGGING_CONTEXT_MANAGER is not None:
        LOGGING_CONTEXT_MANAGER.__exit__(None, None, None)  # pylint: disable=no-member


def pytest_collection_modifyitems(
    session: pytest.Session, config: 'Config', items: List[pytest.Item]
) -> None:
    items.sort(key=lambda item: item.__class__.__name__ == 'IntegrationTestItem')


def pytest_runtest_setup(item: pytest.Function) -> None:
    contexts.clear()
