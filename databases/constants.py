from __future__ import annotations

from pathlib import Path
from typing import List, cast
from typing_extensions import get_args

from lib import pyright
from ._types import SupportedDatabase
from .utils import DatabaseConfig, DatabaseFeature


def _fromdir(path: str) -> list[str]:
    """Get the contents of a subdirectory within the `` directory"""
    # TODO: recurse subdirs
    return [
        str(f.relative_to(TESTS_DIR)) for f in (TESTS_DIR / path).iterdir()
    ]


# databases
CONFIG_MAPPING: dict[SupportedDatabase, DatabaseConfig] = {
    'postgresql': DatabaseConfig(
        id='postgresql',
        name='PostgreSQL',
        env_var='POSTGRESQL_URL',
        bools_are_ints=False,
        unsupported_features=set(),
        id_declarations={
            'base': '@id',
            'cuid': '@id @default(cuid())',
            'autoincrement': '@id @default(autoincrement())',
        },
    ),
    'sqlite': DatabaseConfig(
        id='sqlite',
        name='SQLite',
        env_var='SQLITE_URL',
        bools_are_ints=False,
        unsupported_features={
            'enum',
            'json',
            'arrays',
            'create_many',
            'case_sensitivity',
        },
        id_declarations={
            'base': '@id',
            'cuid': '@id @default(cuid())',
            'autoincrement': '@id @default(autoincrement())',
        },
    ),
    'mysql': DatabaseConfig(
        id='mysql',
        name='MySQL',
        env_var='MYSQL_URL',
        bools_are_ints=True,
        unsupported_features={
            'arrays',
            'case_sensitivity',
        },
        id_declarations={
            'base': '@id',
            'cuid': '@id @default(cuid())',
            'autoincrement': '@id @default(autoincrement())',
        },
    ),
    'mongodb': DatabaseConfig(
        id='mongodb',
        name='MongoDB',
        env_var='MONGODB_URL',
        bools_are_ints=False,
        unsupported_features={
            'decimal',
            'sql_raw_queries',
            'composite_keys',
        },
        id_declarations={
            'cuid': '@id @default(cuid()) @map("_id")',
            'autoincrement': '@id @map("_id")',
            'base': '@id @map("_id")',
        },
    ),
}
SUPPORTED_DATABASES = cast(
    List[SupportedDatabase], list(get_args(SupportedDatabase))
)

# paths
ROOT_DIR = Path(__file__).parent.parent
DATABASES_DIR = Path(__file__).parent

# database features
TESTS_DIR = DATABASES_DIR / 'tests'
FEATURES_MAPPING: dict[DatabaseFeature, list[str]] = {
    # TODO: do not require the "features" split?
    'enum': [
        'test_enum.py',
        'arrays/test_enum.py',
        'composite_keys/test_enum.py',
    ],
    'json': ['types/test_json.py', 'arrays/test_json.py'],
    'decimal': ['types/test_decimal.py', 'arrays/test_decimal.py'],
    'arrays': _fromdir('arrays'),
    'create_many': ['test_create_many.py'],
    'sql_raw_queries': ['test_raw_queries.py', 'models/test_raw_queries.py'],
    'case_sensitivity': ['test_case_sensitivity.py'],
    'composite_keys': _fromdir('composite_keys'),
}

# config files
PYRIGHT_CONFIG: pyright.Config = {
    'include': [
        'tests',
    ],
    'exclude': [],
    # required so that Pyright can resolve the `lib` module
    'extraPaths': ['../'],
    'typeCheckingMode': 'strict',
    'reportPrivateUsage': False,
    # copied from `pyproject.toml`
    'reportUnusedImport': True,
    'reportPrivateUsage': False,
    'reportImportCycles': False,
    'reportUnknownMemberType': False,
    'reportUnknownVariableType': False,
    'reportUnknownArgumentType': False,
    # very strict errors
    'reportUnusedCallResult': False,
    'reportImplicitStringConcatenation': False,
    'reportCallInDefaultInitializer': True,
}
PYTEST_CONFIG = {
    '[tool.pytest.ini_options]': {
        'asyncio_mode': 'strict',
        'ignore': [],
    },
}
