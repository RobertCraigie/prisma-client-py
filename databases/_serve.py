from __future__ import annotations

import shlex
import subprocess

from ._types import SupportedDatabase


def start_database(
    database: SupportedDatabase,
    *,
    version: str | None = None,
) -> None:
    """Start a docker-compose database service"""
    if database == 'sqlite':
        raise ValueError('Cannot start a server for SQLite.')

    args = shlex.split(
        'docker compose -f databases/docker-compose.yml up -d --remove-orphans'
    )
    subprocess.check_call(
        [
            *args,
            f'{database}{_format_version(version)}',
        ]
    )


def _format_version(version: str | None) -> str:
    if version is None:
        return ''

    return '-' + version.replace('.', '-')
