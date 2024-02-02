from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, List, Iterator

import pytest

import prisma
from prisma import Prisma
from prisma.cli import setup_logging
from lib.testing.shared_conftest import *
from lib.testing.shared_conftest.async_client import *

from .utils import Runner, Testdir

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.pytester import Pytester
    from _pytest.monkeypatch import MonkeyPatch


LOGGING_CONTEXT_MANAGER = setup_logging(use_handler=False)


prisma.register(Prisma())

pytest.register_assert_rewrite('tests.test_generation.utils')


@pytest.fixture()
def runner(monkeypatch: 'MonkeyPatch') -> Runner:
    """Fixture for running cli tests"""
    return Runner(patcher=monkeypatch)


@pytest.fixture(name='testdir')
def testdir_fixture(pytester: Pytester) -> Iterator[Testdir]:
    cwd = os.getcwd()
    os.chdir(pytester.path)
    sys.path.insert(0, str(pytester.path))

    yield Testdir(pytester)

    os.chdir(cwd)
    sys.path.remove(str(pytester.path))


# TODO: don't emulate the with statement
def pytest_sessionstart(session: pytest.Session) -> None:
    LOGGING_CONTEXT_MANAGER.__enter__()


def pytest_sessionfinish(session: pytest.Session) -> None:
    if (  # pragma: no branch
        LOGGING_CONTEXT_MANAGER is not None
    ):  # pyright: ignore[reportUnnecessaryComparison]
        LOGGING_CONTEXT_MANAGER.__exit__(None, None, None)


def pytest_collection_modifyitems(session: pytest.Session, config: Config, items: List[pytest.Item]) -> None:
    items.sort(key=lambda item: item.__class__.__name__ == 'IntegrationTestItem')
