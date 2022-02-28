import json
from typing import List
from pathlib import Path
from importlib import import_module

import click

from ..utils import pretty_info
from ... import __version__
from ...binaries import PRISMA_VERSION, ENGINE_VERSION
from ...binaries.platform import binary_platform


@click.command(
    'version', short_help='Display Prisma Client Python version information.'
)
@click.option(
    '--json',
    'output_json',
    is_flag=True,
    help='Output version information in JSON format.',
)
def cli(output_json: bool) -> None:
    """Display Prisma Client Python version information."""
    extras = {
        'dev': 'tox',
        'docs': 'mkdocs',
    }
    installed: List[str] = []
    for extra, module in extras.items():
        try:
            import_module(module)
        except ImportError:
            continue
        else:
            installed.append(extra)

    info = {
        'prisma': PRISMA_VERSION,
        'prisma client python': __version__,
        'platform': binary_platform(),
        'engines': ENGINE_VERSION,
        'install path': str(Path(__file__).resolve().parent.parent.parent),
        'installed extras': installed,
    }

    if output_json:
        click.echo(
            json.dumps(
                {k.replace(' ', '-'): v for k, v in info.items()}, indent=2
            )
        )
    else:
        click.echo(pretty_info(info))
