import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, NamedTuple

import click

from ._node import node, npm
from .. import config
from ..errors import PrismaError


log: logging.Logger = logging.getLogger(__name__)


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
    entrypoint = ensure_cached().entrypoint
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


class CLICache(NamedTuple):
    cache_dir: Path
    entrypoint: Path


def ensure_cached() -> CLICache:
    cache_dir = config.binary_cache_dir
    entrypoint = cache_dir / 'node_modules' / 'prisma' / 'build' / 'index.js'

    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)

    if not entrypoint.exists():
        click.echo('Installing Prisma CLI')
        proc = npm.run(
            'install',
            f'prisma@{config.prisma_version}',
            cwd=config.binary_cache_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if proc.returncode != 0:
            # TODO: test
            click.echo(
                f'An error ocurred while installing the Prisma CLI; npm install log: {proc.stdout.decode("utf-8")}'
            )
            proc.check_returncode()

    if not entrypoint.exists():
        raise PrismaError(
            f'CLI installation appeared to complete but the expected entrypoint ({entrypoint}) could not be found.'
        )

    return CLICache(cache_dir=cache_dir, entrypoint=entrypoint)
