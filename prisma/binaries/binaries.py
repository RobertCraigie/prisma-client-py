# -*- coding: utf-8 -*-

import os
import logging
import tempfile
from pathlib import Path

from . import platform
from .utils import download
from .engine import Engine, ENGINE_VERSION


__all__ = (
    'PRISMA_VERSION',
    'PRISMA_URL',
    'ENGINES',
    'PRISMA_CLI_NAME',
    'GLOBAL_TEMP_DIR',
    'ensure_cached',
)

log = logging.getLogger(__name__)

# hardcode CLI version and engine version
PRISMA_VERSION = '2.12.0'

# CLI binaries are stored here
PRISMA_URL = os.environ.get(
    'PRISMA_CLI_URL',
    'https://prisma-photongo.s3-eu-west-1.amazonaws.com/prisma-cli-{version}-{platform}.gz',
)

ENGINES = [
    Engine(name='query-engine', env='PRISMA_QUERY_ENGINE_BINARY'),
    Engine(name='migration-engine', env='PRISMA_MIGRATION_ENGINE_BINARY'),
    Engine(name='introspection-engine', env='PRISMA_INTROSPECTION_ENGINE_BINARY'),
    Engine(name='prisma-fmt', env='PRISMA_FMT_BINARY'),
]

# local file path for the prisma CL
PRISMA_CLI_NAME = f'prisma-cli-{platform.name()}'

# where the engines live
GLOBAL_TEMP_DIR = (
    Path(tempfile.gettempdir()) / 'prisma' / 'binaries' / 'engines' / ENGINE_VERSION
)


def ensure_cached() -> Path:
    download_cli()

    for engine in ENGINES:
        engine.download()

    return GLOBAL_TEMP_DIR


def download_cli():
    url = PRISMA_URL.format(version=PRISMA_VERSION, platform=platform.name())
    dest = GLOBAL_TEMP_DIR.joinpath(platform.check_for_extension(PRISMA_CLI_NAME))

    if dest.exists():
        log.debug('Prisma cli is cached')
    else:
        log.info('Downloading the Prisma cli, this may take a few minutes...')
        download(url, str(dest.absolute()))
        log.info('Finished downloading Prisma cli')
        log.debug('Downloaded prisma cli to %s', dest.absolute())
