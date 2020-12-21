# -*- coding: utf-8 -*-

import os
import platform
import tempfile
from pathlib import Path

from .types import Engine


__all__ = (
    'PRISMA_VERSION',
    'ENGINE_VERSION',
    'PRISMA_URL',
    'ENGINE_URL',
    'ENGINES',
    'PRISMA_CLI_NAME',
    'GLOBAL_TEMP_DIR',
    'GLOBAL_UNPACK_DIR',
)


# hardcode CLI version and engine version
PRISMA_VERSION = '2.12.0'

# versions can be found under https://github.com/prisma/prisma-engine/commits/master
ENGINE_VERSION = '58369335532e47bdcec77a2f1e7c1fb83a463918'

# CLI binaries are stored here
PRISMA_URL = os.environ.get(
    'PRISMA_CLI_URL', 'https://prisma-photongo.s3-eu-west-1.amazonaws.com/%s-%s-%s.gz'
)

# engine binaries are stored here
ENGINE_URL = os.environ.get(
    'PRISMA_ENGINE_URL', 'https://binaries.prisma.sh/all_commits/%s/%s/%s.gz'
)
ENGINES = [
    Engine(name='query-engine', env='PRISMA_QUERY_ENGINE_BINARY'),
    Engine(name='migration-engine', env='PRISMA_MIGRATION_ENGINE_BINARY'),
    Engine(name='introspection-engine', env='PRISMA_INTROSPECTION_ENGINE_BINARY'),
    Engine(name='prisma-fmt', env='PRISMA_FMT_BINARY'),
]

# local file path for the prisma CLI
PRISMA_CLI_NAME = f'prisma-cl-{platform.system().lower()}'

# where the engines live
GLOBAL_TEMP_DIR = (
    Path(tempfile.gettempdir()) / 'prisma' / 'binaries' / 'engines' / ENGINE_VERSION
)

GLOBAL_UNPACK_DIR = GLOBAL_TEMP_DIR.joinpath('unpacked')
