import os
import sys
import json
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import Generic, Dict, Type, Any, Optional, cast

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from . import jsonrpc
from .jsonrpc import Manifest
from .models import DefaultData, PythonData
from .types import PartialModelFields
from .utils import (
    copy_tree,
    is_same_path,
    resolve_template_path,
)
from .. import __version__
from ..utils import DEBUG_GENERATOR
from .._compat import cached_property
from .._types import BaseModelT, InheritsGeneric, get_args


__all__ = (
    'BASE_PACKAGE_DIR',
    'GenericGenerator',
    'BaseGenerator',
    'Generator',
    'render_template',
    'cleanup_templates',
    'partial_models_ctx',
)

log: logging.Logger = logging.getLogger(__name__)
BASE_PACKAGE_DIR = Path(__file__).parent.parent
GENERIC_GENERATOR_NAME = 'prisma.generator.generator.GenericGenerator'

# set of templates that should be rendered after every other template
DEFERRED_TEMPLATES = {'partials.py.jinja'}

DEFAULT_ENV = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(Path(__file__).parent / 'templates'),
)
partial_models_ctx: ContextVar[Dict[str, PartialModelFields]] = ContextVar(
    'partial_models_ctx', default={}
)


class GenericGenerator(ABC, Generic[BaseModelT]):
    @abstractmethod
    def get_manifest(self) -> Manifest:
        """Get the metadata for this generator

        This is used by prisma to display the post-generate message e.g.

        ✔ Generated Prisma Client Python to ./.venv/lib/python3.9/site-packages/prisma
        """
        ...

    @abstractmethod
    def generate(self, data: BaseModelT) -> None:
        ...

    @classmethod
    def invoke(cls) -> None:
        """Shorthand for calling BaseGenerator().run()"""
        generator = cls()
        generator.run()

    def run(self) -> None:
        """Run the generation loop

        This can only be called from a prisma generation, e.g.

        ```prisma
        generator client {
            provider = "python generator.py"
        }
        ```
        """
        if not os.environ.get('PRISMA_GENERATOR_INVOCATION'):
            raise RuntimeError(
                'Attempted to invoke a generator outside of Prisma generation'
            )

        while True:
            line = jsonrpc.readline()
            if line is None:
                log.debug('Prisma invocation ending')
                break

            request = jsonrpc.parse(line)

            # TODO: this can hang the prisma process if an error occurs
            response = None
            if request.method == 'getManifest':
                response = jsonrpc.Response(
                    id=request.id,
                    result=dict(
                        manifest=self.get_manifest(),
                    ),
                )
            elif request.method == 'generate':
                if request.params is None:  # pragma: no cover
                    raise RuntimeError(
                        'Prisma JSONRPC did not send data to generate.'
                    )

                if DEBUG_GENERATOR:
                    _write_debug_data(
                        'params', json.dumps(request.params, indent=2)
                    )

                data = self.data_class.parse_obj(request.params)

                if DEBUG_GENERATOR:
                    _write_debug_data('data', data.json(indent=2))

                self.generate(data)
                response = jsonrpc.Response(id=request.id, result=None)
            else:  # pragma: no cover
                raise RuntimeError(
                    f'JSON RPC received unexpected method: {request.method}'
                )

            if response is not None:
                jsonrpc.reply(response)

    @cached_property
    def data_class(self) -> Type[BaseModelT]:
        """Return the BaseModel used to parse the Prisma DMMF"""

        # we need to cast to object as otherwise pyright correctly marks the code as unreachable,
        # this is because __orig_bases__ is not present in the typeshed stubs as it is
        # intended to be for internal use only, however I could not find a method
        # for resolving generic TypeVars for inherited subclasses without using it.
        # please create an issue or pull request if you know of a solution.
        cls = cast(object, self.__class__)
        if not isinstance(cls, InheritsGeneric):
            raise RuntimeError('Could not resolve generic type arguments.')

        typ: Optional[Any] = None
        for base in cls.__orig_bases__:
            if base.__origin__ == GenericGenerator:
                typ = base
                break

        if typ is None:  # pragma: no cover
            raise RuntimeError(
                'Could not find the GenericGenerator type;\n'
                'This should never happen;\n'
                f'Does {cls} inherit from {GenericGenerator} ?'
            )

        args = get_args(typ)
        if not args:
            raise RuntimeError(
                f'Could not resolve generic arguments from type: {typ}'
            )

        model = args[0]
        if not issubclass(model, BaseModel):
            raise TypeError(
                f'Expected first generic type argument argument to be a subclass of {BaseModel} '
                f'but got {model} instead.'
            )

        # we know the type we have resolved is the same as the first generic argument
        # passed to GenericGenerator, safe to cast
        return cast(Type[BaseModelT], model)


class BaseGenerator(GenericGenerator[DefaultData]):
    pass


class Generator(GenericGenerator[PythonData]):
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        raise TypeError(
            f'{Generator} cannot be subclassed, maybe you meant {BaseGenerator}?'
        )

    def get_manifest(self) -> Manifest:
        return Manifest(
            name=f'Prisma Client Python (v{__version__})',
            default_output=BASE_PACKAGE_DIR,
        )

    def generate(self, data: PythonData) -> None:
        config = data.generator.config
        rootdir = Path(data.generator.output.value)
        if not rootdir.exists():
            rootdir.mkdir(parents=True, exist_ok=True)

        if not is_same_path(BASE_PACKAGE_DIR, rootdir):
            copy_tree(BASE_PACKAGE_DIR, rootdir)

        params = data.to_params()

        try:
            for name in DEFAULT_ENV.list_templates():
                if (
                    not name.endswith('.py.jinja')
                    or name.startswith('_')
                    or name in DEFERRED_TEMPLATES
                ):
                    continue

                render_template(rootdir, name, params)

            if config.partial_type_generator:
                log.debug('Generating partial types')
                config.partial_type_generator.run()

            params['partial_models'] = partial_models_ctx.get()
            for name in DEFERRED_TEMPLATES:
                render_template(rootdir, name, params)
        except:
            cleanup_templates(rootdir, env=DEFAULT_ENV)
            raise

        log.debug('Finished generating Prisma Client Python')


def cleanup_templates(
    rootdir: Path, *, env: Optional[Environment] = None
) -> None:
    """Revert module to pre-generation state"""
    if env is None:
        env = DEFAULT_ENV

    for name in env.list_templates():
        file = resolve_template_path(rootdir=rootdir, name=name)
        if file.exists():
            log.debug('Removing rendered template at %s', file)
            file.unlink()


def render_template(
    rootdir: Path,
    name: str,
    params: Dict[str, Any],
    *,
    env: Optional[Environment] = None,
) -> None:
    if env is None:
        env = DEFAULT_ENV

    template = env.get_template(name)
    output = template.render(**params)

    file = resolve_template_path(rootdir=rootdir, name=name)
    if not file.parent.exists():
        file.parent.mkdir(parents=True, exist_ok=True)

    file.write_bytes(output.encode(sys.getdefaultencoding()))
    log.debug('Rendered template to %s', file.absolute())


def _write_debug_data(name: str, output: str) -> None:
    path = Path(__file__).parent.joinpath(f'debug-{name}.json')

    with path.open('w') as file:
        file.write(output)

    log.debug('Wrote generator %s to %s', name, path.absolute())
