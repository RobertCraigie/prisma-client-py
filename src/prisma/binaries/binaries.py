# -*- coding: utf-8 -*-

import logging
import os
import tempfile
from pathlib import Path
from typing import Callable, List, Optional

import click
from pydantic import BaseSettings, Field

from . import platform
from .download import download

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

# Get system information
OS_SETTINGS: platform.OsSettings = platform.get_os_settings()
PLATFORM: str = platform.resolve_platform(OS_SETTINGS)
CLI_PLATFORM: str = OS_SETTINGS.system

# TODO: if this version changes but the engine version
#       doesn't change then the CLI is incorrectly cached
# hardcoded CLI version version
PRISMA_VERSION: str = '3.8.1'

# versions can be found under https://github.com/prisma/prisma-engine/commits/main
ENGINE_VERSION = os.environ.get(
    'PRISMA_ENGINE_VERSION', '34df67547cf5598f5a6cd3eb45f14ee70c3fb86f'
)
GLOBAL_TEMP_DIR: Path = (
    Path(tempfile.gettempdir()) / 'prisma' / 'binaries' / 'engines' / ENGINE_VERSION
)
PLATFORM_EXE_EXTENSION: str = ".exe" if OS_SETTINGS.is_windows() else ""


def default_in_temp(name: str) -> Callable[[], Path]:
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


settings: PrismaSettings = PrismaSettings()


PRISMA_CLI_NAME = f"prisma-cli-{PRISMA_VERSION}-{CLI_PLATFORM}{PLATFORM_EXE_EXTENSION}"
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

    def download(self) -> None:
        download(self.url, self.path)

    def remove(self) -> None:
        # This might fail if file is still in use, which happens during tests (somehow)!
        self.path.unlink(missing_ok=True)


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
            log.debug(f"%s is cached, skipping download" % binary.name)
            continue
        log.debug(f"%s is not cached, will download" % binary.name)
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
            log.debug("Downloading %s from %s" % (binary.name, binary.url))
            binary.download()

    return GLOBAL_TEMP_DIR


def remove_all() -> None:
    """Remove all downloaded binaries"""
    for binary in BINARIES:
        binary.remove()
