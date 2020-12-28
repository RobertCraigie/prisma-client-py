import os
import logging
import tempfile
from pathlib import Path
from pydantic import BaseModel

from . import platform
from .utils import download


__all__ = (
    'Engine',
    'ENGINE_VERSION',
    'ENGINE_URL',
    'GLOBAL_TEMP_DIR',
)

log = logging.getLogger(__name__)

# engine binaries are stored here
ENGINE_URL = os.environ.get(
    'PRISMA_ENGINE_URL', 'https://binaries.prisma.sh/all_commits/{0}/{1}/{2}.gz'
)

# versions can be found under https://github.com/prisma/prisma-engine/commits/master
ENGINE_VERSION = '58369335532e47bdcec77a2f1e7c1fb83a463918'

# where the engines live
GLOBAL_TEMP_DIR = (
    Path(tempfile.gettempdir()) / 'prisma' / 'binaries' / 'engines' / ENGINE_VERSION
)


class Engine(BaseModel):
    name: str
    env: str

    def download(self):
        binary_name = platform.binary_platform()
        log.debug('Checking engine %s', self.name)

        to = self.location
        url = platform.check_for_extension(
            ENGINE_URL.format(ENGINE_VERSION, binary_name, self.name)
        )

        if to.exists():
            log.debug('%s is cached', to)
            return

        log.info('Downloading %s, this may take a few minutes...', self.name)
        log.debug('Downloading from %s to %s', url, to)
        download(url, str(to.absolute()))
        log.debug('%s download finished', self.name)

    @property
    def location(self) -> str:
        env = os.environ.get(self.env)
        if env is not None:
            log.debug('Using environment variable location: %s for %s', env, self.name)
            return env

        binary_name = platform.binary_platform()
        return platform.check_for_extension(
            GLOBAL_TEMP_DIR.joinpath(f'prisma-{self.name}-{binary_name}')
        )
