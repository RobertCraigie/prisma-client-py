from __future__ import annotations

from typing import List, cast
from pathlib import Path
from typing_extensions import get_args

from lib import pyright

from .utils import DatabaseConfig, DatabaseFeature
from ._types import DatabaseMapping, SupportedDatabase


def _fromdir(path: str) -> list[str]:
    """Get the contents of a subdirectory within the `` directory"""
    # TODO: recurse subdirs
    return [str(f.relative_to(TESTS_DIR)) for f in (TESTS_DIR / path).iterdir()]


# databases
CONFIG_MAPPING: DatabaseMapping[DatabaseConfig] = {
    'postgresql': DatabaseConfig(
        id='postgresql',
        name='PostgreSQL',
        env_var='POSTGRESQL_URL',
        bools_are_ints=False,
        unsupported_features=set(),
        default_date_func='CURRENT_DATE',
        autoincrement_id='Int @id @default(autoincrement())',
    ),
    'cockroachdb': DatabaseConfig(
        id='cockroachdb',
        name='CockroachDB',
        env_var='COCKROACHDB_URL',
        bools_are_ints=False,
        default_date_func='CURRENT_DATE',
        autoincrement_id='BigInt @id @default(sequence())',
        unsupported_features={
            'json_arrays',
            'array_push',
            'transactions',
        },
    ),
    'sqlite': DatabaseConfig(
        id='sqlite',
        name='SQLite',
        env_var='SQLITE_URL',
        bools_are_ints=False,
        default_date_func='',
        autoincrement_id='Int @id @default(autoincrement())',
        unsupported_features={
            'enum',
            'json',
            'date',
            'arrays',
            'create_many',
            'case_sensitivity',
        },
    ),
    'mysql': DatabaseConfig(
        id='mysql',
        name='MySQL',
        env_var='MYSQL_URL',
        bools_are_ints=True,
        default_date_func='(CURRENT_DATE)',
        autoincrement_id='Int @id @default(autoincrement())',
        unsupported_features={
            'arrays',
            'case_sensitivity',
        },
    ),
    'mariadb': DatabaseConfig(
        id='mysql',
        name='MariaDB',
        env_var='MARIADB_URL',
        bools_are_ints=True,
        default_date_func='CURRENT_DATE',
        autoincrement_id='Int @id @default(autoincrement())',
        unsupported_features={
            'arrays',
            'case_sensitivity',
        },
    ),
}
SUPPORTED_DATABASES = cast(List[SupportedDatabase], list(get_args(SupportedDatabase)))

# paths
ROOT_DIR = Path(__file__).parent.parent
DATABASES_DIR = Path(__file__).parent

# database features
TESTS_DIR = DATABASES_DIR / 'tests'
SYNC_TESTS_DIR = DATABASES_DIR / 'sync_tests'
FEATURES_MAPPING: dict[DatabaseFeature, list[str]] = {
    'enum': ['test_enum.py', 'test_arrays/test_enum.py'],
    'json': [
        'types/test_json.py',
        'test_arrays/test_json.py',
        'types/raw_queries/test_json.py',
    ],
    'arrays': [*_fromdir('arrays'), *_fromdir('types/raw_queries/arrays')],
    'array_push': _fromdir('arrays/push'),
    'json_arrays': ['arrays/test_json.py', 'arrays/push/test_json.py'],
    'transactions': ['test_transactions.py'],
    # not yet implemented
    'date': [],
    'create_many': ['test_create_many.py'],
    'raw_queries': ['test_raw_queries.py', *_fromdir('types/raw_queries')],
    'case_sensitivity': ['test_case_sensitivity.py'],
}

# config files
PYRIGHT_CONFIG: pyright.Config = {
    'include': [],
    'exclude': ['../src/prisma/_vendor/**.py', '**/prisma/_vendor/**.py'],
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
    'reportImplicitOverride': True,
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
