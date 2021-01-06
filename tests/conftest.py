# pylint: disable=global-statement
import asyncio

import pytest
import prisma
from prisma.cli import setup_logging

from .utils import async_run


CLIENT = None
LOGGING_CONTEXT_MANAGER = None


@pytest.fixture
def client() -> prisma.Client:
    global CLIENT

    if CLIENT is None:
        CLIENT = prisma.Client()
        async_run(CLIENT.connect())

    # TODO: this should reset the database state before every test
    return CLIENT


@pytest.fixture
def event_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


# TODO: don't emulate the with statement
def pytest_sessionstart(session: pytest.Session) -> None:
    global LOGGING_CONTEXT_MANAGER
    LOGGING_CONTEXT_MANAGER = setup_logging(use_handler=False)
    LOGGING_CONTEXT_MANAGER.__enter__()  # pylint: disable=no-member


def pytest_sessionfinish(session: pytest.Session) -> None:
    if LOGGING_CONTEXT_MANAGER is not None:
        LOGGING_CONTEXT_MANAGER.__exit__(None, None, None)  # pylint: disable=no-member
