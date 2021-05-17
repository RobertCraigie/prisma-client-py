import sys
import logging
from pathlib import Path
from typing import Optional, Any

import click

from .. import prisma, options
from ..utils import EnumChoice, PathlibPath, should_pipe
from ...generator.models import HttpChoices, TransformChoices


ARG_TO_CONFIG_KEY = {
    'transform': 'transform_fields',
    'partials': 'partial_type_generator',
}

log = logging.getLogger(__name__)


@click.command('generate')
@options.schema
@options.watch
@click.option(
    '--skip-plugins/--use-plugins',
    is_flag=True,
    default=None,
    help='Whether or not to skip running prisma plugins',
)
@click.option(
    '--http',
    type=EnumChoice(HttpChoices),
    help='HTTP client library the generated client will use',
)
@click.option(
    '--transform',
    type=EnumChoice(TransformChoices),
    help='How to transform model fields to python case',
)
@click.option(
    '--partials',
    type=PathlibPath(exists=True, readable=True),
    help="Partial type generator location",
)
def cli(schema: Optional[Path], watch: bool, **kwargs: Any) -> None:
    """Generate prisma artifacts with modified config options"""
    args = ['generate']
    if schema is not None:
        args.append(f'--schema={schema}')

    if watch:
        args.append('--watch')

    env = {}
    prefix = 'PRISMA_PY_CONFIG_'
    for key, value in kwargs.items():
        if value is None:
            continue

        env[prefix + ARG_TO_CONFIG_KEY.get(key, key).upper()] = serialize(key, value)

    log.debug('Running generate with env: %s', env)
    sys.exit(prisma.run(args, env=env, pipe=should_pipe()))


def serialize(key: str, obj: Any) -> str:
    if key == 'partials':
        # partials has to be JSON serializable
        return f'"{obj}"'
    return str(obj)
