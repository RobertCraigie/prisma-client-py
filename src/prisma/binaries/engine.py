import os
import logging
from pathlib import Path

from . import platform
from .binary import Binary
from .. import config


__all__ = ('Engine',)

log: logging.Logger = logging.getLogger(__name__)


class Engine(Binary):
    name: str
    env: str

    @property
    def url(self) -> str:
        return platform.check_for_extension(
            config.engine_url.format(
                config.engine_version, platform.binary_platform(), self.name
            )
        )

    @property
    def path(self) -> Path:
        env = os.environ.get(self.env)
        if env is not None:
            log.debug(
                'Using environment variable location: %s for %s',
                env,
                self.name,
            )
            return Path(env)

        binary_name = platform.binary_platform()
        return Path(
            platform.check_for_extension(
                str(
                    config.binary_cache_dir.joinpath(
                        f'prisma-{self.name}-{binary_name}'
                    )
                )
            )
        )
