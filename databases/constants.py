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
    ),
    'cockroachdb': DatabaseConfig(
        id='postgresql',
        name='CockroachDB',
        env_var='COCKROACHDB_URL',
        bools_are_ints=False,
        unsupported_features={
            'json_arrays',
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
    ),
    'mariadb': DatabaseConfig(
        id='mysql',
        name='MariaDB',
        env_var='MARIADB_URL',
        bools_are_ints=True,
        unsupported_features={
            'arrays',
            'case_sensitivity',
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
    'enum': ['test_enum.py', 'test_arrays/test_enum.py'],
    'json': ['types/test_json.py', 'test_arrays/test_json.py'],
    'arrays': _fromdir('arrays'),
    'json_arrays': ['arrays/test_json.py'],
    'create_many': ['test_create_many.py'],
    'raw_queries': ['test_raw_queries.py'],
    'case_sensitivity': ['test_case_sensitivity.py'],
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
