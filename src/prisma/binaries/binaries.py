# -*- coding: utf-8 -*-

import logging
import os
import subprocess
import tempfile
from pathlib import Path
import time
from typing import Callable, List, Optional, Tuple

import click
from pydantic import BaseSettings, Field
from prisma.errors import PrismaError

from prisma.utils import time_since


from . import platform
from .download import download

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
PLATFORM_EXE_EXTENSION: str = '.exe' if OS_SETTINGS.is_windows() else ''

PRISMA_CLI_NAME = f'prisma-cli-{PRISMA_VERSION}-{CLI_PLATFORM}{PLATFORM_EXE_EXTENSION}'


def default_prisma_cli_path() -> Path:
    return GLOBAL_TEMP_DIR / PRISMA_CLI_NAME


def default_engine_path(name: str) -> Callable[[], Path]:
    return lambda: (GLOBAL_TEMP_DIR / name).with_suffix(PLATFORM_EXE_EXTENSION)


class PrismaSettings(BaseSettings):
    PRISMA_CLI_MIRROR: str = 'https://prisma-photongo.s3-eu-west-1.amazonaws.com'
    PRISMA_ENGINES_MIRROR: str = 'https://binaries.prisma.sh'

    PRISMA_QUERY_ENGINE_BINARY: Path = Field(
        default_factory=default_engine_path('query-engine')
    )
    PRISMA_MIGRATION_ENGINE_BINARY: Path = Field(
        default_factory=default_engine_path('migration-engine')
    )
    PRISMA_INTROSPECTION_ENGINE_BINARY: Path = Field(
        default_factory=default_engine_path('introspection-engine')
    )
    PRISMA_CLI_BINARY: Path = Field(default_factory=default_prisma_cli_path)
    PRISMA_FMT_BINARY: Path = Field(default_factory=default_engine_path('prisma-fmt'))
    PRISMA_CLI_BINARY_TARGETS: List[str] = Field(default_factory=list)

    def engine_url(self, name: str) -> str:
        return (
            f'{self.PRISMA_ENGINES_MIRROR}/'
            'all_commits/'
            f'{ENGINE_VERSION}/'
            f'{PLATFORM}/'
            f'{name}{PLATFORM_EXE_EXTENSION}.gz'
        )

    def prisma_cli_url(self) -> str:
        return f'{self.PRISMA_CLI_MIRROR}/{PRISMA_CLI_NAME}.gz'


SETTINGS: PrismaSettings = PrismaSettings()


log: logging.Logger = logging.getLogger(__name__)


class InvalidBinaryVersion(PrismaError):
    pass


class Binary:
    name: str
    url: str
    path: Path
    settings: PrismaSettings

    def __init__(
        self,
        name: str,
        path: Path,
        *,
        url: Optional[str] = None,
        settings: Optional[PrismaSettings] = None,
    ):
        if settings is None:
            settings = SETTINGS
        self.settings = settings
        self.name = name
        self.path = path
        self.url = settings.engine_url(name) if url is None else url

    def download(self) -> None:
        download(self.url, self.path)

    def remove(self) -> None:
        # This might fail if file is still in use, which happens during tests (somehow)!
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    def ensure_binary(self) -> None:
        """
        If binary doesn't exist or is not a file, raise an error

        Args:
            binary (Binary): a binary to check
        """
        if not self.path.exists():
            raise FileNotFoundError(
                f'{self.name} binary not found at {self.path}\nTry running `prisma fetch`'
            )
        if not self.path.is_file():
            raise IsADirectoryError(f'{self.name} binary is a directory')
        # Run binary with --version to check if it's the right version and capture stdout
        start_version = time.monotonic()
        process = subprocess.run(
            [str(self.path), '--version'], stdout=subprocess.PIPE, check=True
        )
        log.debug('Version check took %s', time_since(start_version))

        # Version format is: "<name-splitted-with-dashes> <version>"
        # e.g. migration-engine-cli 34df67547cf5598f5a6cd3eb45f14ee70c3fb86f
        # or   query-engine 34df67547cf5598f5a6cd3eb45f14ee70c3fb86f
        version = process.stdout.decode().split(' ')[1]
        if version != ENGINE_VERSION:
            raise InvalidBinaryVersion(
                f'{self.name} binary version {version} is not {ENGINE_VERSION}'
            )


EnginesType = Tuple[
    Binary,  # query-engine
    Binary,  # migration-engine
    Binary,  # introspection-engine
    Binary,  # prisma-fmt
]

# Maybe we should use a dict instead of a tuple? or a namedtuple?
BinariesType = Tuple[
    Binary,  # query-engine
    Binary,  # migration-engine
    Binary,  # introspection-engine
    Binary,  # prisma-fmt
    Binary,  # prisma-cli
]


def engines_from_settings(
    settings: PrismaSettings,
) -> EnginesType:
    return (
        Binary(name='query-engine', path=settings.PRISMA_QUERY_ENGINE_BINARY),
        Binary(name='migration-engine', path=settings.PRISMA_MIGRATION_ENGINE_BINARY),
        Binary(
            name='introspection-engine',
            path=settings.PRISMA_INTROSPECTION_ENGINE_BINARY,
        ),
        Binary(name='prisma-fmt', path=settings.PRISMA_FMT_BINARY),
    )


def binaries_from_settings(
    settings: PrismaSettings, *, engines: Optional[EnginesType] = None
) -> BinariesType:
    if engines is None:
        engines = engines_from_settings(settings)
    return (
        *engines,
        Binary(
            name='prisma-cli',
            path=settings.PRISMA_CLI_BINARY,
            url=settings.prisma_cli_url(),
        ),
    )


ENGINES: EnginesType = engines_from_settings(SETTINGS)

BINARIES: BinariesType = binaries_from_settings(SETTINGS, engines=ENGINES)


def ensure_cached() -> Path:
    to_download: List[Binary] = []
    for binary in BINARIES:
        if binary.path.exists():
            log.debug('%s is cached, skipping download', binary.name)
            continue
        log.debug('%s is not cached, will download', binary.name)
        to_download.append(binary)

    if len(to_download) == 0:
        log.debug('All binaries are cached, skipping download')
        return GLOBAL_TEMP_DIR

    def show_item(item: Optional[Binary]) -> str:
        return '' if item is None else item.name

    with click.progressbar(
        to_download,
        label='Downloading binaries',
        fill_char=click.style('#', fg='yellow'),
        item_show_func=show_item,
    ) as iterator:
        for binary in iterator:
            log.debug('Downloading %s from %s', binary.name, binary.url)
            binary.download()

    return GLOBAL_TEMP_DIR


def remove_all() -> None:
    """Remove all downloaded binaries"""
    for binary in BINARIES:
        binary.remove()
