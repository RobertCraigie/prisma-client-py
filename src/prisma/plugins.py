import logging
from typing import (
    Optional,
    Iterator,
    Union,
    Any,
    TypeVar,
    Type,
    Callable,
    overload,
    cast,
)

import pkg_resources
from pydantic import BaseModel

from ._types import Literal
from .utils import _NoneType
from .errors import PluginMissingRequiredHookError


log: logging.Logger = logging.getLogger(__name__)

__all__ = ('PluginContext', 'load_plugins')


T = TypeVar('T')
Hook = Callable[..., Any]
Method = Literal['generate']
HookName = Literal[Method]


class PluginContext(BaseModel):
    method: Method
    data: 'Data'

    def run(self) -> None:
        for plugin in load_plugins(self):
            plugin.run_hook(self.method, self, default=None)

    def __str__(self) -> str:
        return f'<PluginContext method\'{self.method}\' data={"output hidden" if self.data else None}>'


class Plugin:
    obj: Any
    ctx: PluginContext
    entry: pkg_resources.EntryPoint

    def __init__(
        self, *, entry: pkg_resources.EntryPoint, obj: Any, ctx: PluginContext
    ) -> None:
        self.entry = entry
        self.obj = obj
        self.ctx = ctx

    def get_hook(self, name: HookName) -> Optional[Hook]:
        attr = 'prisma_' + name

        try:
            hook = getattr(self.obj, attr)
        except AttributeError:
            log.debug('Plugin %s does not define a %s hook', self.name, attr)
            return None

        if not callable(hook):
            raise TypeError(
                f'Hook at {self.entry.module_name}.{attr} is not callable, '
                f'got {type(hook)} instead.'
            )

        # mypy doesn't recognise the callable check we do
        return cast(Hook, hook)

    @overload
    def run_hook(
        self,
        name: HookName,
        *args: Any,
        default: Any = _NoneType,
    ) -> Any:
        ...

    @overload
    def run_hook(
        self,
        name: HookName,
        *args: Any,
        default: Any = _NoneType,
        typecheck: Type[T],
    ) -> T:
        ...

    def run_hook(
        self,
        name: HookName,
        *args: Any,
        default: Any = _NoneType,
        typecheck: Optional[Type[T]] = None,
    ) -> Union[T, Any]:
        log.debug('Running hook %s on entry %s', name, self.name)
        hook = self.get_hook(name)

        if hook is None:
            if default is not _NoneType:
                return default

            raise PluginMissingRequiredHookError(
                f'Plugin {self.name} is missing a {name} hook.'
            )

        # TODO: validate arguments
        ret = hook(*args)
        log.debug('Hook %s on entry %s returned %s', name, self.name, ret)

        if typecheck is not None:
            if not isinstance(ret, typecheck):
                raise TypeError(
                    f'Expected {self.name} plugin hook {hook} '
                    f'to return {typecheck} but got {type(ret)} instead.'
                )

        return ret

    @property
    def name(self) -> str:
        return self.entry.name

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'<Plugin entry="{self.entry}" obj={self.obj} ctx={self.ctx}>'


def load_plugins(ctx: PluginContext) -> Iterator[Plugin]:
    for entry in pkg_resources.iter_entry_points('prisma'):
        log.debug(
            'Loading entry point %s pointing to %s', entry.name, entry.module_name
        )
        obj = entry.load()
        yield Plugin(entry=entry, obj=obj, ctx=ctx)


# circular import
from .generator.models import (  # pylint: disable=unused-import, wrong-import-position
    Data,
)

PluginContext.update_forward_refs()
