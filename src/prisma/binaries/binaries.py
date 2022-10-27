# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from typing import Optional, List

import click

from .binary import Binary
from .engine import Engine
from .constants import PRISMA_CLI_NAME
from .. import config, utils


__all__ = (
    'ENGINES',
    'BINARIES',
    'ensure_cached',
    'remove_all',
)

log: logging.Logger = logging.getLogger(__name__)

PRISMA_FORMAT_BINARY = Engine(name='prisma-fmt', env='PRISMA_FMT_BINARY')

ENGINES: List[Engine] = [
    Engine(name='query-engine', env='PRISMA_QUERY_ENGINE_BINARY'),
    Engine(name='migration-engine', env='PRISMA_MIGRATION_ENGINE_BINARY'),
    Engine(
        name='introspection-engine', env='PRISMA_INTROSPECTION_ENGINE_BINARY'
    ),
    PRISMA_FORMAT_BINARY,
]

BINARIES: List[Binary] = [
    *ENGINES,
    Binary(name=PRISMA_CLI_NAME, env='PRISMA_CLI_BINARY'),
]


def ensure_cached() -> Path:
    undownloaded_binaries: List[Binary] = []
    for binary in BINARIES:
        path = binary.path
        if path.exists():
            log.debug('%s cached at %s', binary.name, path)
        else:
            log.debug('%s not cached at %s', binary.name, path)
            undownloaded_binaries.append(binary)

    if not undownloaded_binaries:
        log.debug('All binaries are cached')
        return config.binary_cache_dir

    def show_item(item: Optional[Binary]) -> str:
        if item is not None:
            if utils.DEBUG:
                return f'{binary.name} ({binary.url})'
            else:
                return binary.name
        return ''

    with click.progressbar(
        undownloaded_binaries,
        label='Downloading binaries',
        fill_char=click.style('#', fg='yellow'),
        item_show_func=show_item,
    ) as iterator:
        for binary in iterator:
            binary.download()

    return config.binary_cache_dir


def remove_all() -> None:
    """Remove all downloaded binaries"""
    for binary in BINARIES:
        if binary.path.exists():
            binary.path.unlink()
