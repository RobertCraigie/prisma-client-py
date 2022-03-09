# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from typing import Optional, List

import click

from .binary import Binary
from .engine import Engine
from .constants import GLOBAL_TEMP_DIR, PRISMA_CLI_NAME


__all__ = (
    'ENGINES',
    'BINARIES',
    'ensure_cached',
    'remove_all',
)

log: logging.Logger = logging.getLogger(__name__)

ENGINES = [
    Engine(name='query-engine', env='PRISMA_QUERY_ENGINE_BINARY'),
    Engine(name='migration-engine', env='PRISMA_MIGRATION_ENGINE_BINARY'),
    Engine(
        name='introspection-engine', env='PRISMA_INTROSPECTION_ENGINE_BINARY'
    ),
    Engine(name='prisma-fmt', env='PRISMA_FMT_BINARY'),
]

BINARIES: List[Binary] = [
    *ENGINES,
    Binary(name=PRISMA_CLI_NAME, env='PRISMA_CLI_BINARY'),
]


def ensure_cached() -> Path:
    binaries: List[Binary] = []
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

    def show_item(item: Optional[Binary]) -> str:
        if item is not None:
            return binary.name
        return ''

    with click.progressbar(
        binaries,
        label='Downloading binaries',
        fill_char=click.style('#', fg='yellow'),
        item_show_func=show_item,
    ) as iterator:
        for binary in iterator:
            binary.download()

    return GLOBAL_TEMP_DIR


def remove_all() -> None:
    """Remove all downloaded binaries"""
    for binary in BINARIES:
        if binary.path.exists():
            binary.path.unlink()
