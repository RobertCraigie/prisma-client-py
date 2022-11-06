from __future__ import annotations

from pathlib import Path
from typing import List, cast
from typing_extensions import get_args

from lib import pyright
from ._types import SupportedDatabase
from .utils import DatabaseConfig, DatabaseFeature


def _fromdir(path: str) -> list[str]:
    """Get the contents of a subdirectory within the `features` directory"""
    # TODO: recurse subdirs
    return [
        str(f.relative_to(FEATURES_DIR))
        for f in (FEATURES_DIR / path).iterdir()
    ]


# databases
CONFIG_MAPPING: dict[SupportedDatabase, DatabaseConfig] = {
    'postgresql': DatabaseConfig(
        id='postgresql',
        name='PostgreSQL',
        env_var='POSTGRESQL_URL',
        unsupported_features=set(),
    ),
    'sqlite': DatabaseConfig(
        id='sqlite',
        name='SQLite',
        env_var='SQLITE_URL',
        unsupported_features={
            'enum',
            'json',
            'arrays',
            'create_many',
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
FEATURES_DIR = DATABASES_DIR / 'tests' / 'features'
FEATURES_MAPPING: dict[DatabaseFeature, list[str]] = {
    'enum': ['test_enum.py', 'test_arrays/test_enum.py'],
    'json': ['test_json.py', 'test_arrays/test_json.py'],
    'arrays': _fromdir('test_arrays'),
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
