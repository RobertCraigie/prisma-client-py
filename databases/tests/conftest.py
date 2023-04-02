import os

import pytest

import prisma
from prisma import Prisma

from lib.testing.shared_conftest import *
from lib.testing.shared_conftest.async_client import *
from ..utils import DatabaseConfig, RAW_QUERIES_MAPPING, RawQueries


prisma.register(Prisma())


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
