import os
import sys
import logging
import subprocess
from textwrap import indent
from typing import List, Optional, Dict

import click

from .. import binaries


log: logging.Logger = logging.getLogger(__name__)


def run(
    args: List[str],
    check: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> int:
    directory = binaries.ensure_cached()
    path = directory.joinpath(binaries.PRISMA_CLI_NAME)
    if not path.exists():
        raise RuntimeError(
            f'The Prisma CLI is not downloaded, expected {path} to exist.'
        )

    log.debug('Using Prisma CLI at %s', path)
    log.debug('Running prisma command with args: %s', args)

    default_env = {
        **os.environ,
        'PRISMA_HIDE_UPDATE_MESSAGE': 'true',
        'PRISMA_CLI_QUERY_ENGINE_TYPE': 'binary',
    }
    env = {**default_env, **env} if env is not None else default_env
    # ensure the client uses our engine binaries
    for engine in binaries.ENGINES:
        env[engine.env] = str(engine.path.absolute())

    if args and args[0] == 'studio':
        click.echo(
            click.style(
                'ERROR: Prisma Studio does not work natively with Prisma Client Python',
                fg='red',
            ),
        )
        click.echo(
            '\nThere are two other possible ways to use Prisma Studio:\n'
        )
        click.echo(
            click.style('1. Download the Prisma Studio app\n', bold=True)
        )
        click.echo(
            indent(
                'Prisma Studio can be downloaded from: '
                + click.style(
                    'https://github.com/prisma/studio/releases', underline=True
                ),
                ' ' * 3,
            )
        )
        click.echo(
            click.style('\n2. Use the Node based Prisma CLI:\n', bold=True)
        )
        click.echo(
            indent(
                'If you have Node / NPX installed you can launch Prisma Studio by running the command: ',
                ' ' * 3,
            ),
            nl=False,
        )
        click.echo(click.style('npx prisma studio', bold=True))
        return 1

    process = subprocess.run(
        [str(path.absolute()), *args],
        env=env,
        check=check,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    if args and args[0] in {'--help', '-h'}:
        prefix = ' '
        click.echo(click.style(prefix + 'Python Commands\n', bold=True))
        click.echo(
            prefix
            + 'For Prisma Client Python commands see '
            + click.style('prisma py --help', bold=True)
        )

    return process.returncode
