from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Union, Optional, List

import tomlkit
from pydantic import BaseSettings, Extra, Field

from ._proxy import LazyProxy

if TYPE_CHECKING:
    from pydantic.env_settings import SettingsSourceCallable


class DefaultConfig(BaseSettings):
    # CLI version
    # TODO: if this version changes but the engine version
    #       doesn't change then the CLI is incorrectly cached
    prisma_version: str = Field(
        env='PRISMA_VERSION',
        default='4.11.0',
    )

    # Engine binary versions can be found under https://github.com/prisma/prisma-engine/commits/main
    expected_engine_version: str = Field(
        env='PRISMA_EXPECTED_ENGINE_VERSION',
        default='8fde8fef4033376662cad983758335009d522acb',
    )

    # Home directory, used to build the `binary_cache_dir` option by default, useful in multi-user
    # or testing environments so that the binaries can be easily cached without having to worry
    # about versioning them.
    home_dir: Path = Field(
        env='PRISMA_HOME_DIR',
        default=Path.home(),
    )

    # Where to store the downloaded binaries
    binary_cache_dir: Union[Path, None] = Field(
        env='PRISMA_BINARY_CACHE_DIR',
        default=None,
    )

    # Workaround to support setting the binary platform until it can be properly implemented
    binary_platform: Optional[str] = Field(
        env='PRISMA_BINARY_PLATFORM', default=None
    )

    # Whether or not to use the global node installation (if available)
    use_global_node: bool = Field(env='PRISMA_USE_GLOBAL_NODE', default=True)

    # Whether or not to use the `nodejs-bin` package (if installed)
    use_nodejs_bin: bool = Field(env='PRISMA_USE_NODEJS_BIN', default=True)

    # Extra arguments to pass to nodeenv, arguments are passed after the path, e.g. python -m nodeenv <path> <extra args>
    nodeenv_extra_args: List[str] = Field(
        env='PRISMA_NODEENV_EXTRA_ARGS',
        default_factory=list,
    )

    # Where to download nodeenv to, defaults to ~/.cache/prisma-python/nodeenv
    nodeenv_cache_dir: Path = Field(
        env='PRISMA_NODEENV_CACHE_DIR',
        default_factory=lambda: Path.home()
        / '.cache'
        / 'prisma-python'
        / 'nodeenv',
    )

    class Config(BaseSettings.Config):
        extra: Extra = Extra.ignore

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            # prioritise env settings over init settings
            return env_settings, init_settings, file_secret_settings


class Config(DefaultConfig):
    binary_cache_dir: Path = Field(env='PRISMA_BINARY_CACHE_DIR')

    @classmethod
    def from_base(cls, config: DefaultConfig) -> Config:
        if config.binary_cache_dir is None:
            config.binary_cache_dir = (
                config.home_dir
                / '.cache'
                / 'prisma-python'
                / 'binaries'
                / config.prisma_version
                / config.expected_engine_version
            )

        return cls.parse_obj(config.dict())

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        if path is None:
            path = Path('pyproject.toml')

        if path.exists():
            config = (
                tomlkit.loads(path.read_text())
                .get('tool', {})
                .get('prisma', {})
            )
        else:
            config = {}

        return cls.parse(**config)

    @classmethod
    def parse(cls, **kwargs: object) -> Config:
        return cls.from_base(DefaultConfig.parse_obj(kwargs))


class LazyConfigProxy(LazyProxy[Config]):
    def __load__(self) -> Config:
        return Config.load()


config: Config = LazyConfigProxy().__as_proxied__()
