from __future__ import annotations

import shlex
from pathlib import Path

import nox

from ._types import SupportedDatabase


SCRIPTS = Path(__file__).parent / 'scripts'
DOCKER_COMPOSE_FILE = Path(__file__).parent / 'docker-compose.yml'


def start_database(
    database: SupportedDatabase,
    *,
    version: str | None,
    session: nox.Session,
) -> None:
    """Start a docker-compose database service"""
    if database == 'sqlite':
        raise ValueError('Cannot start a server for SQLite.')

    if database == 'mongodb':
        script = SCRIPTS / 'start-mongodb.sh'
        session.log(f'Running script at {script}')
        session.run_always(str(script))
        return

    args = shlex.split(
        f'docker compose -f {DOCKER_COMPOSE_FILE} up -d --remove-orphans'
    )
    session.run_always(
        *args,
        f'{database}{_format_version(version)}',
        external=True,
    )


def _format_version(version: str | None) -> str:
    if version is None:
        return ''

    return '-' + version.replace('.', '-')
