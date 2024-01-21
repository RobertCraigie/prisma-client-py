import os

import pytest
from syrupy.assertion import SnapshotAssertion

import prisma
from prisma import Prisma
from prisma._compat import model_parse_json
from lib.testing.shared_conftest import *
from lib.testing.shared_conftest.async_client import *

from ..utils import (
    RAW_QUERIES_MAPPING,
    RawQueries,
    DatabaseConfig,
    AmberSharedExtension,
)

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
    return model_parse_json(DatabaseConfig, os.environ['DATABASE_CONFIG'])


@pytest.fixture()
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.use_extension(AmberSharedExtension)
