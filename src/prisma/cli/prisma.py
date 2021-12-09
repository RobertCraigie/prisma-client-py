import os
import sys
import logging
import subprocess
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
    if env is not None:
        env = {**default_env, **env}
    else:
        env = default_env

    # ensure the client uses our engine binaries
    for engine in binaries.ENGINES:
        env[engine.env] = str(engine.path.absolute())

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
