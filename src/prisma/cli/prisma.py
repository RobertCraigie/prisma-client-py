import os
import subprocess
from subprocess import CompletedProcess
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict

import click

# from nodejs import npm, node

from ._node import node, npm
from ..binaries import PRISMA_VERSION, ENGINE_VERSION


log: logging.Logger = logging.getLogger(__name__)


CACHE_DIR = Path(
    os.environ.get(
        'PRISMA_PY_CACHE_DIR',
        Path.home()
        / '.cache'
        / 'prisma-binaries'
        / PRISMA_VERSION
        / ENGINE_VERSION,
    )
)
CLI_ENTRYPOINT = CACHE_DIR / 'node_modules' / 'prisma' / 'build' / 'index.js'


def run(
    args: List[str],
    check: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> int:
    log.debug('Running prisma command with args: %s', args)

    default_env = {
        **os.environ,
        'PRISMA_HIDE_UPDATE_MESSAGE': 'true',
        'PRISMA_CLI_QUERY_ENGINE_TYPE': 'binary',
    }
    env = {**default_env, **env} if env is not None else default_env

    # TODO: ensure graceful termination

    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True)

    node.install()

    entrypoint = CLI_ENTRYPOINT
    if not entrypoint.exists():
        # TODO: output that installing CLI is happening?
        click.echo('Installing Prisma CLI')
        proc = npm.run(
            'install',
            f'prisma@{PRISMA_VERSION}',
            cwd=CACHE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if proc.returncode != 0:
            print('npm install log: ', proc.stdout)
            proc.check_returncode()

    if not entrypoint.exists():
        raise RuntimeError('TODO: better error message and class')

    process = node.run(
        str(entrypoint),
        *args,
        env=env,
        check=check,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    if args and args[0] in {'--help', '-h'}:
        click.echo(click.style('Python Commands\n', bold=True))
        click.echo(
            '  '
            + 'For Prisma Client Python commands run '
            + click.style('prisma py --help', bold=True)
        )

    return process.returncode
