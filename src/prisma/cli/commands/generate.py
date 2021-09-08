import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import click
import pydantic

from .. import prisma, options
from ..utils import EnumChoice, PathlibPath, warning
from ...generator.models import InterfaceChoices


ARG_TO_CONFIG_KEY = {
    'partials': 'partial_type_generator',
}

log: logging.Logger = logging.getLogger(__name__)


@click.command('generate')
@options.schema
@options.watch
@click.option(
    '--interface',
    type=EnumChoice(InterfaceChoices),
    help='Method that the client will use to interface with Prisma',
)
@click.option(
    '--partials',
    type=PathlibPath(exists=True, readable=True),
    help='Partial type generator location',
)
def cli(schema: Optional[Path], watch: bool, **kwargs: Any) -> None:
    """Generate prisma artifacts with modified config options"""
    if pydantic.VERSION.split('.') < ['1', '8']:
        warning(
            'Unsupported version of pydantic installed, this command may not work as intended\n'
            'Please update pydantic to 1.8 or greater.\n'
        )

    args = ['generate']
    if schema is not None:
        args.append(f'--schema={schema}')

    if watch:
        args.append('--watch')

    env: Dict[str, str] = {}
    prefix = 'PRISMA_PY_CONFIG_'
    for key, value in kwargs.items():
        if value is None:
            continue

        env[prefix + ARG_TO_CONFIG_KEY.get(key, key).upper()] = serialize(key, value)

    log.debug('Running generate with env: %s', env)
    sys.exit(prisma.run(args, env=env))


def serialize(key: str, obj: Any) -> str:
    if key == 'partials':
        # partials has to be JSON serializable
        return f'"{obj}"'
    return str(obj)
