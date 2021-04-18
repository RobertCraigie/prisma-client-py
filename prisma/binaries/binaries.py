# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from typing import Optional

from .binary import Binary
from .engine import Engine
from .constants import GLOBAL_TEMP_DIR, PRISMA_CLI_NAME


__all__ = (
    'ENGINES',
    'BINARIES',
    'ensure_cached',
)

log = logging.getLogger(__name__)

ENGINES = [
    Engine(name='query-engine', env='PRISMA_QUERY_ENGINE_BINARY'),
    Engine(name='migration-engine', env='PRISMA_MIGRATION_ENGINE_BINARY'),
    Engine(name='introspection-engine', env='PRISMA_INTROSPECTION_ENGINE_BINARY'),
    Engine(name='prisma-fmt', env='PRISMA_FMT_BINARY'),
]

BINARIES = [
    *ENGINES,
    Binary(name=PRISMA_CLI_NAME),
]


def ensure_cached() -> Path:
    binaries = []
    for binary in BINARIES:
        path = binary.path
        if path.exists():
            log.debug('%s cached at %s', binary.name, path)
        else:
            log.debug('%s not cached at %s', binary.name, path)
            binaries.append(binary)

    if not binaries:
        log.debug('All binaries are cached')
        return GLOBAL_TEMP_DIR

    for binary in binaries:
        binary.download()

    return GLOBAL_TEMP_DIR
