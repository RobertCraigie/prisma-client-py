import logging
import inspect
import importlib
from types import ModuleType
from typing import TYPE_CHECKING, Union, Any, Iterator, Optional, List, cast

from . import errors
from .models import Data
from .types import Manifest
from .._types import TypedDict, Protocol, Literal

"""
if TYPE_CHECKING:
    # circular imports
    from .config import Config
"""

log = logging.getLogger(__name__)


class Plugin(TypedDict):
    id: str
    once: bool
    module: str


# the hooks are typed to return Any in order to enforce runtime type checking


class GenerateHook(Protocol):
    # should return PluginsResult
    def __call__(self, data: Data) -> Any:
        ...


class ManifestHook(Protocol):
    # should return Manifest
    def __call__(self) -> Any:
        ...


class PluginModuleRequiredType(ModuleType):
    generate: GenerateHook


class PluginModuleOptionalType(PluginModuleRequiredType):
    manifest: ManifestHook


PluginModuleType = Union[PluginModuleRequiredType, PluginModuleOptionalType]


def _validate_module(module: ModuleType) -> None:
    if not hasattr(module, 'generate'):
        raise errors.PluginMissingHookError(
            f'plugin: {module.__name__} is missing a generate function'
        )

    hook = module.generate  # type: ignore[attr-defined]
    spec = inspect.getfullargspec(hook)
    if len(spec.args) != 1:
        raise errors.PluginInvalidHookError(
            f'Expected {module.__name__} plugin to take 1 argument but got got {len(spec.args)} instead'
        )


class PluginModule:
    def __init__(self, module: ModuleType) -> None:
        _validate_module(module)
        self.module = cast(PluginModuleType, module)

    def manifest(self) -> Manifest:
        if not self.has_manifest():
            raise errors.PluginMissingHookError(
                f'plugin: {self.module.__name__} is missing a manifest function'
            )

        # safe type ignore as mypy doesn't register
        # that we check if the attr exists
        result = self.module.manifest()  # type: ignore[union-attr]

        if not isinstance(result, Manifest):
            raise errors.PluginMismatchedTypeError(
                f'plugin {self.module.__name__}.manifest returned {type(result)} expected {Manifest}'
            )

        return result

    def has_manifest(self) -> bool:
        return hasattr(self.module, 'manifest')

    def generate(self, data: Data) -> 'PluginsResult':
        result = self.module.generate(data)
        if not isinstance(result, PluginsResult):
            raise errors.PluginMismatchedTypeError(
                f'plugin {self.module.__name__}.generate returned {type(result)} expected {PluginsResult}'
            )

        return result


def _resolve_plugin(plugin: Union[Plugin, str]) -> PluginModule:
    if not isinstance(plugin, str):
        name = plugin['module']
    else:
        name = plugin

    log.debug('Importing plugin %s', name)
    return PluginModule(importlib.import_module(name))


import os
import json
import uuid
import atexit
from pathlib import Path


Key = Literal['plugins']


class ConfigType(TypedDict, total=False):
    plugins: List[Plugin]


class Config:
    def __init__(self) -> None:
        self._db = {}  # type: ConfigType
        self.file = Path(__file__).parent / 'config.json'
        self.filename = str(self.file.absolute())
        self.load()

    def load(self) -> None:
        if not self.file.exists():
            self._db = {}
        else:
            self._db = json.loads(self.file.read_text())

    def save(self) -> None:
        # TODO: is this method really necessary?
        tmp_file = f'{self.filename}-{uuid.uuid4()}.tmp'
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(self._db.copy(), f, ensure_ascii=True, indent=2)

        os.replace(tmp_file, self.filename)

    def get(self, key: Literal['plugins']) -> List[Plugin]:
        return self._db.get(key, cast(List[Plugin], []))

    def put(self, key: Literal['plugins'], value: List[Plugin]) -> None:
        self._db[key] = value
        self.save()

    def __repr__(self) -> str:
        return f'<Config {self._db.__repr__()}>'


class Plugins:
    def __init__(self) -> None:
        self.config = Config()

        # list of plugin IDs added in the current process
        self.__plugins: List[str] = []
        atexit.register(self.__del__)

    def __del__(self) -> None:
        plugins = self.config.get('plugins')
        for plugin_id in self.__plugins:
            plugins = list(filter(lambda p: p['id'] != plugin_id, plugins))

        self.config.put('plugins', plugins)

    def add(self, module: str, *, once: bool) -> None:
        plugin_id = str(uuid.uuid4())
        self.config.get('plugins').append(
            {'module': module, 'once': once, 'id': plugin_id}
        )
        self.config.save()
        self.__plugins.append(plugin_id)

    def run(self, data: Data) -> 'PluginsResult':
        result = PluginsResult()
        plugins = self.config.get('plugins')
        for plugin in plugins:
            if plugin['once']:
                self.config.put(
                    'plugins', list(filter(lambda p: p['id'] != plugin['id'], plugins))
                )

            result.update(self._run_plugin(plugin, data))

        return result

    def _run_plugin(self, plugin: Plugin, data: Data) -> 'PluginsResult':
        name = plugin['module']
        lib = _resolve_plugin(name)
        log.debug('Running plugin %s', name)
        result = lib.generate(data)
        log.debug('Plugin %s returned %s', name, result)
        return result

    def __iter__(self) -> Iterator[PluginModule]:
        plugins = self.config.get('plugins')
        for plugin in plugins:
            yield _resolve_plugin(plugin)


class PluginsResult:
    def __init__(self, end: bool = False) -> None:
        self.end = end

    def update(self, new: 'PluginsResult') -> None:
        self.end = new.end

    def __str__(self) -> str:
        return f'<PluginsResult end={self.end}>'

    def __repr__(self) -> str:
        return str(self)


plugins = Plugins()
