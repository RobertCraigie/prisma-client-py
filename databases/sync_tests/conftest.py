from __future__ import annotations

import os

import pytest

from lib.testing.shared_conftest import *
from lib.testing.shared_conftest.sync_client import *

from ..utils import RAW_QUERIES_MAPPING, RawQueries, DatabaseConfig


# TODO: the async tests conftest.py is imported somehow which breaks this...
# prisma.register(Prisma())


# TODO: better error messages for invalid state
@pytest.fixture(name='database')
def database_fixture() -> str:
    return os.environ['PRISMA_DATABASE']


@pytest.fixture(name='raw_queries')
def raw_queries_fixture(database: str) -> RawQueries:
    return RAW_QUERIES_MAPPING[database]


@pytest.fixture(name='config', scope='session')
def config_fixture() -> DatabaseConfig:
    return DatabaseConfig.parse_raw(os.environ['DATABASE_CONFIG'])
