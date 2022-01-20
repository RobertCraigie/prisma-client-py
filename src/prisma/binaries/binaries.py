# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from typing import Optional, List

import click


import os
import tempfile
from pathlib import Path
from typing import List

from prisma.binaries.download import download

from . import platform


# PLATFORMS: List[str] = [
#     'darwin',
#     'darwin-arm64',
#     'debian-openssl-1.0.x',
#     'debian-openssl-1.1.x',
#     'rhel-openssl-1.0.x',
#     'rhel-openssl-1.1.x',
#     'linux-arm64-openssl-1.1.x',
#     'linux-arm64-openssl-1.0.x',
#     'linux-arm-openssl-1.1.x',
#     'linux-arm-openssl-1.0.x',
#     'linux-musl',
#     'linux-nixos',
#     'windows',
#     'freebsd11',
#     'freebsd12',
#     'openbsd',
#     'netbsd',
#     'arm',
# ]

PLATFORM = platform.get_platform()

from pydantic import BaseSettings, Field


# TODO: if this version changes but the engine version
#       doesn't change then the CLI is incorrectly cached
# hardcoded CLI version version
PRISMA_VERSION = '3.7.0'

# versions can be found under https://github.com/prisma/prisma-engine/commits/main
ENGINE_VERSION = os.environ.get(
    'PRISMA_ENGINE_VERSION', '8746e055198f517658c08a0c426c7eec87f5a85f'
)
GLOBAL_TEMP_DIR = (
    Path(tempfile.gettempdir()) / 'prisma' / 'binaries' / 'engines' / ENGINE_VERSION
)
PLATFORM_EXE_EXTENSION = ".exe" if PLATFORM == "windows" else ""


def default_in_temp(name: str):
    return lambda: (GLOBAL_TEMP_DIR / name).with_suffix(PLATFORM_EXE_EXTENSION)


class PrismaSettings(BaseSettings):
    PRISMA_CLI_MIRROR: str = "https://prisma-photongo.s3-eu-west-1.amazonaws.com"
    PRISMA_ENGINES_MIRROR: str = "https://binaries.prisma.sh"
    PRISMA_QUERY_ENGINE_BINARY: Path = Field(
        default_factory=default_in_temp("query-engine")
    )
    PRISMA_MIGRATION_ENGINE_BINARY: Path = Field(
        default_factory=default_in_temp("migration-engine")
    )
    PRISMA_INTROSPECTION_ENGINE_BINARY: Path = Field(
        default_factory=default_in_temp("introspection-engine")
    )
    PRISMA_FMT_BINARY: Path = Field(default_factory=default_in_temp("prisma-fmt"))
    PRISMA_CLI_BINARY_TARGETS: List[str] = Field(default_factory=list)


settings = PrismaSettings()

# CLI binaries are stored here
PRISMA_CLI_NAME = f"prisma-cli-{PRISMA_VERSION}-{PLATFORM}{PLATFORM_EXE_EXTENSION}"
PRISMA_CLI_PATH = GLOBAL_TEMP_DIR / PRISMA_CLI_NAME
PRISMA_CLI_URL = f"{settings.PRISMA_CLI_MIRROR}/{PRISMA_CLI_NAME}.gz"


def engine_url_for(name: str) -> str:
    return f"{settings.PRISMA_ENGINES_MIRROR}/all_commits/{ENGINE_VERSION}/{PLATFORM}/{name}{PLATFORM_EXE_EXTENSION}.gz"


log: logging.Logger = logging.getLogger(__name__)


class Binary:
    name: str
    url: str
    path: Path

    def __init__(self, name: str, path: Path, *, url: Optional[str] = None):
        self.name = name
        self.path = path
        self.url = engine_url_for(name) if url is None else url


ENGINES: List[Binary] = [
    Binary(name='query-engine', path=settings.PRISMA_QUERY_ENGINE_BINARY),
    Binary(name='migration-engine', path=settings.PRISMA_MIGRATION_ENGINE_BINARY),
    Binary(
        name='introspection-engine', path=settings.PRISMA_INTROSPECTION_ENGINE_BINARY
    ),
    Binary(name='prisma-fmt', path=settings.PRISMA_FMT_BINARY),
]

BINARIES: List[Binary] = [
    *ENGINES,
    Binary(name="prisma-cli", path=PRISMA_CLI_PATH, url=PRISMA_CLI_URL),
]


def ensure_cached() -> Path:
    to_download: List[Binary] = []
    for binary in BINARIES:
        if binary.path.exists():
            log.debug(f"{binary.name} is cached, skipping download")
            continue
        log.debug(f"{binary.name} is not cached, will download")
        to_download.append(binary)

    if len(to_download) == 0:
        log.debug("All binaries are cached, skipping download")
        return GLOBAL_TEMP_DIR

    def show_item(item: Optional[Binary]) -> str:
        return "" if item is None else item.name

    with click.progressbar(
        to_download,
        label='Downloading binaries',
        fill_char=click.style('#', fg='yellow'),
        item_show_func=show_item,
    ) as iterator:
        for binary in iterator:
            print(f"Downloading {binary.url}")
            download(binary.url, binary.path)

    return GLOBAL_TEMP_DIR


def remove_all() -> None:
    """Remove all downloaded binaries"""
    for binary in BINARIES:
        if binary.path.exists():
            binary.path.unlink()
