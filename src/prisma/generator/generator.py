import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from contextvars import ContextVar
from distutils.dir_util import copy_tree

from jinja2 import Environment, FileSystemLoader

from .models import Data
from .types import PartialModelFields
from .utils import is_same_path, resolve_template_path, resolve_original_file

from ..utils import DEBUG_GENERATOR


__all__ = (
    'BASE_PACKAGE_DIR',
    'run',
    'render_template',
    'cleanup_templates',
    'partial_models_ctx',
)

log: logging.Logger = logging.getLogger(__name__)
BASE_PACKAGE_DIR = Path(__file__).parent.parent

# set of templates that should be rendered after every other template
DEFERRED_TEMPLATES = {'partials.py.jinja'}

# set of templates that override existing modules
OVERRIDING_TEMPLATES = {'http.py.jinja'}

DEFAULT_ENV = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(Path(__file__).parent / 'templates'),
)
partial_models_ctx: ContextVar[Dict[str, PartialModelFields]] = ContextVar(
    'partial_models_ctx', default={}
)


def run(params: Dict[str, Any]) -> None:
    if DEBUG_GENERATOR:
        _write_debug_data('params', json.dumps(params, indent=2))

    data = Data.parse_obj(params)
    config = data.generator.config

    if DEBUG_GENERATOR:
        _write_debug_data('data', data.json(indent=2))

    rootdir = Path(data.generator.output.value)
    if not rootdir.exists():
        rootdir.mkdir(parents=True, exist_ok=True)

    if not is_same_path(BASE_PACKAGE_DIR, rootdir):
        copy_tree(str(BASE_PACKAGE_DIR), str(rootdir))

    params = vars(data)

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

    log.debug('Finished generating the prisma python client')


def cleanup_templates(rootdir: Path, *, env: Optional[Environment] = None) -> None:
    """Revert module to pre-generation state"""
    if env is None:
        env = DEFAULT_ENV

    for name in env.list_templates():
        file = resolve_template_path(rootdir=rootdir, name=name)
        original = resolve_original_file(file)
        if original.exists():
            if file.exists():
                log.debug('Removing overridden template at %s', file)
                file.unlink()

            log.debug('Renaming file at %s to %s', original, file)
            original.rename(file)
        elif file.exists() and name not in OVERRIDING_TEMPLATES:
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

    if name in OVERRIDING_TEMPLATES and file.exists():
        original = resolve_original_file(file)
        if not original.exists():
            log.debug('Making backup of %s', file)
            file.rename(original)

    file.write_bytes(output.encode(sys.getdefaultencoding()))
    log.debug('Rendered template to %s', file.absolute())


def _write_debug_data(name: str, output: str) -> None:
    path = Path(__file__).parent.joinpath(f'debug-{name}.json')

    with path.open('w') as file:
        file.write(output)

    log.debug('Wrote generator %s to %s', name, path.absolute())
