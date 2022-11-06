import os

import pytest

import prisma
from prisma import Prisma

from lib.testing.shared_conftest import *
from .utils import RAW_QUERIES_MAPPING, RawQueries
from ..utils import DatabaseConfig


prisma.register(Prisma())


# TODO: better error messages for invalid state
@pytest.fixture(name='datasource')
def datasource_fixture() -> str:
    return os.environ['PRISMA_DATABASE']


@pytest.fixture(name='raw_queries')
def raw_queries_fixture(datasource: str) -> RawQueries:
    return RAW_QUERIES_MAPPING[datasource]


@pytest.fixture(name='config', scope='session')
def config_fixture() -> DatabaseConfig:
    return DatabaseConfig.parse_raw(os.environ['DATABASE_CONFIG'])
