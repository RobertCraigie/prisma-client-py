from __future__ import annotations
from functools import cached_property

import json
import shlex
import shutil
from pathlib import Path
from copy import deepcopy
from contextvars import ContextVar, copy_context
from typing import (
    Iterable,
    List,
    Optional,
    cast,
)

import nox
import yaml
import click
import rtoml
import typer
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from lib.utils import flatten
from prisma._compat import cached_property

from .utils import DatabaseConfig
from .types import SupportedDatabase
from .constants import (
    SUPPORTED_DATABASES,
    DATABASES_DIR,
    CONFIG_MAPPING,
    ROOT_DIR,
    PYTEST_CONFIG,
    FEATURES_MAPPING,
    PYRIGHT_CONFIG,
    FEATURES_DIR,
)


# TODO: switch to a pretty logging setup
# structlog?

session_ctx: ContextVar[nox.Session] = ContextVar('session_ctx')


# TODO: proper progname in help
cli = typer.Typer(
    help='Test suite for testing Prisma Client Python against different database providers.',
)


@cli.command()
def main(
    *,
    databases: list[str] = SUPPORTED_DATABASES,
    inplace: bool = False,
    pytest_args: Optional[str] = None,
    lint: bool = True,
    test: bool = True,
) -> None:
    """Run unit tests and Pyright"""
    session = session_ctx.get()
    databases = validate_databases(databases)

    with session.chdir(DATABASES_DIR):
        # setup env
        session.install('pyright', '-r', 'requirements.txt')
        if inplace:
            # useful for updating the generated code so that Pylance picks it up
            session.install('-U', '-e', '..')
        else:
            session.install('-U', '..')

        session.run('python', '-m', 'prisma', 'py', 'version')

        for database in databases:
            print(title(CONFIG_MAPPING[database].name))
            runner = Runner(database=database)
            runner.setup()

            if test:
                runner.test(pytest_args=pytest_args)

            if lint:
                runner.lint()


class Runner:
    database: SupportedDatabase
    session: nox.Session
    config: DatabaseConfig
    cache_dir: Path

    def __init__(self, *, database: SupportedDatabase) -> None:
        self.database = database
        self.session = session_ctx.get()
        self.config = CONFIG_MAPPING[database]
        self.cache_dir = ROOT_DIR / '.tests_cache' / 'databases' / database

    def _create_cache_dir(self) -> None:
        cache_dir = self.cache_dir
        if cache_dir.exists():
            shutil.rmtree(cache_dir)

        cache_dir.mkdir(parents=True, exist_ok=True)

    def setup(self) -> None:
        # TODO: split up more
        print('database config: ' + self.config.json(indent=2))

        exclude_files = self.exclude_files
        if exclude_files:
            print(f'excluding files:\n{yaml.dump(list(exclude_files))}')
        else:
            print('excluding files: []')

        self._create_cache_dir()

        # TODO: only create this if linting
        create_pyright_config(self.pyright_config, exclude=exclude_files)

        # TODO: only create this if testing
        pytest_config = self.cache_dir / 'pyproject.toml'
        rtoml.dump(PYTEST_CONFIG, pytest_config, pretty=True)

        # create a Prisma Schema file
        env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            loader=FileSystemLoader(DATABASES_DIR / 'templates'),
        )
        template = env.get_template('schema.prisma.jinja2')
        self.schema.write_text(
            template.render(
                # template variables
                config=self.config,
                partial_generator=(DATABASES_DIR / 'partials.py').absolute(),
            )
        )

        # generate the client
        self.session.run(
            'python',
            '-m',
            'prisma',
            'generate',
            f'--schema={self.schema}',
        )

    def test(self, *, pytest_args: str | None) -> None:
        # ensure DB is in correct state
        self.session.run(
            'python',
            '-m',
            'prisma',
            'db',
            'push',
            '--force-reset',
            '--accept-data-loss',
            '--skip-generate',
            f'--schema={self.schema}',
        )

        args = []
        if pytest_args is not None:
            args = shlex.split(pytest_args)

        # TODO: use PYTEST_ADDOPTS instead
        self.session.run(
            'pytest',
            *args,
            *map(
                lambda i: f'--ignore={i}',
                self.exclude_files,
            ),
            env={
                'PRISMA_DATABASE': self.database,
                # TODO: this should be accessible in the core client
                'DATABASE_CONFIG': self.config.json(),
            },
        )

    def lint(self) -> None:
        self.session.run('pyright', '-p', str(self.pyright_config.absolute()))

    @property
    def pyright_config(self) -> Path:
        # TODO: move this to the cache dir, it requires some clever path renaming
        # as Pyright requires that `exclude` be relative to the location of the config file
        return DATABASES_DIR.joinpath(f'{self.database}.pyrightconfig.json')

    @property
    def schema(self) -> Path:
        return self.cache_dir.joinpath('schema.prisma')

    @cached_property
    def exclude_files(self) -> set[str]:
        files = [
            feature_relpath(path)
            for path in flatten(
                [
                    FEATURES_MAPPING[feature]
                    for feature in self.config.unsupported_features
                ]
            )
        ]
        return set(files)


def validate_databases(databases: list[str]) -> list[SupportedDatabase]:
    for database in databases:
        if database not in SUPPORTED_DATABASES:
            raise ValueError(f'Unknown database: {database}')

    return cast(List[SupportedDatabase], databases)


def feature_relpath(path: str) -> str:
    return str((FEATURES_DIR / path).relative_to(DATABASES_DIR))


def title(text: str) -> str:
    # TODO: improve formatting
    dashes = '-' * 30
    return dashes + ' ' + click.style(text, bold=True) + ' ' + dashes


def create_pyright_config(file: Path, exclude: Iterable[str]) -> None:
    pyright_config = deepcopy(PYRIGHT_CONFIG)
    pyright_config['exclude'].extend(exclude)
    file.write_text(json.dumps(pyright_config, indent=2))


def entrypoint(session: nox.Session) -> None:
    """Wrapper over `cli()` that sets a `session` context variable for easier usage."""

    def wrapper() -> None:
        session_ctx.set(session)
        cli(session.posargs)

    # copy the current context so that the session object is not leaked
    ctx = copy_context()
    return ctx.run(wrapper)


if __name__ == '__main__':
    cli()
