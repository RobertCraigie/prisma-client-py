import os
import logging
from pathlib import Path

from . import platform
from .binary import Binary
from .constants import ENGINE_URL, ENGINE_VERSION, GLOBAL_TEMP_DIR


__all__ = ('Engine',)

log: logging.Logger = logging.getLogger(__name__)


class Engine(Binary):
    name: str
    env: str

    @property
    def url(self) -> str:
        return platform.check_for_extension(
            ENGINE_URL.format(ENGINE_VERSION, platform.binary_platform(), self.name)
        )

    @property
    def path(self) -> Path:
        env = os.environ.get(self.env)
        if env is not None:
            log.debug('Using environment variable location: %s for %s', env, self.name)
            return Path(env)

        binary_name = platform.binary_platform()
        return Path(
            platform.check_for_extension(
                str(GLOBAL_TEMP_DIR.joinpath(f'prisma-{self.name}-{binary_name}'))
            )
        )
