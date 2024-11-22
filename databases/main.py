from __future__ import annotations

import os
import re
import json
import shlex
import shutil
import contextlib
from copy import deepcopy
from typing import (
    Iterator,
    Optional,
    cast,
)
from pathlib import Path
from contextvars import ContextVar, copy_context

import nox
import yaml
import click
import rtoml
import typer
from jinja2 import Environment, StrictUndefined, FileSystemLoader
from nox.command import CommandFailed

from lib.utils import flatten, escape_path
from prisma._compat import model_copy, model_json, cached_property
from pipelines.utils import (
    setup_coverage,
    get_pkg_location,
    maybe_install_nodejs_bin,
)

from .utils import DatabaseConfig
from ._serve import start_database
from ._types import SupportedDatabase
from .constants import (
    ROOT_DIR,
    TESTS_DIR,
    DATABASES_DIR,
    PYTEST_CONFIG,
    CONFIG_MAPPING,
    PYRIGHT_CONFIG,
    SYNC_TESTS_DIR,
    FEATURES_MAPPING,
    SUPPORTED_DATABASES,
)

# TODO: switch to a pretty logging setup
# structlog?

session_ctx: ContextVar[nox.Session] = ContextVar('session_ctx')


# TODO: proper progname in help
cli = typer.Typer(
    help='Test suite for testing Prisma Client Python against different database providers.',
)


@cli.command()
def test(
    *,
    databases: list[str] = cast('list[str]', SUPPORTED_DATABASES),  # pyright: ignore[reportCallInDefaultInitializer]
    exclude_databases: list[str] = [],  # pyright: ignore[reportCallInDefaultInitializer]
    inplace: bool = False,
    pytest_args: Optional[str] = None,
    lint: bool = True,
    test: bool = True,
    coverage: bool = False,
    pydantic_v2: bool = True,
    for_async: bool = typer.Option(default=True, is_flag=False),  # pyright: ignore[reportCallInDefaultInitializer]
) -> None:
    """Run unit tests and Pyright"""
    if not pydantic_v2:
        lint = False

    session = session_ctx.get()

    exclude = set(validate_databases(exclude_databases))
    validated_databases: list[SupportedDatabase] = [
        database for database in validate_databases(databases) if database not in exclude
    ]

    with session.chdir(DATABASES_DIR):
        _setup_test_env(session, pydantic_v2=pydantic_v2, inplace=inplace)

        for database in validated_databases:
            print(title(CONFIG_MAPPING[database].name))

            # point coverage to store data in a database specific location
            # as to not overwrite any existing data from other database tests
            if coverage:  # pragma: no branch
                setup_coverage(session, identifier=database)

            runner = Runner(database=database, track_coverage=coverage, for_async=for_async)
            runner.setup()

            if test:  # pragma: no branch
                runner.test(pytest_args=pytest_args)

            if lint:  # pragma: no branch
                runner.lint()


@cli.command()
def serve(database: str, *, version: Optional[str] = None) -> None:
    """Start a database server using docker-compose"""
    database = validate_database(database)
    start_database(database, version=version, session=session_ctx.get())


@cli.command(name='test-inverse')
def test_inverse(
    *,
    databases: list[str] = cast('list[str]', SUPPORTED_DATABASES),  # pyright: ignore[reportCallInDefaultInitializer]
    coverage: bool = False,
    inplace: bool = False,
    pytest_args: Optional[str] = None,
    pydantic_v2: bool = True,
    for_async: bool = typer.Option(default=True, is_flag=False),  # pyright: ignore[reportCallInDefaultInitializer]
) -> None:
    """Ensure unsupported features actually result in either:

    - Prisma Schema validation failing
    - Our unit tests & linters fail
    """
    session = session_ctx.get()
    validated_databases = validate_databases(databases)

    with session.chdir(DATABASES_DIR):
        _setup_test_env(session, pydantic_v2=pydantic_v2, inplace=inplace)

        for database in validated_databases:
            config = CONFIG_MAPPING[database]
            print(title(config.name))

            if not config.unsupported_features:
                print(f'There are no unsupported features for {database}.')
                continue

            # point coverage to store data in a database specific location
            # as to not overwrite any existing data from other database tests
            if coverage:  # pragma: no branch
                setup_coverage(session, identifier=database)

            # TODO: support for tesing a given list of unsupported features
            for feature in config.unsupported_features:
                print(title(f'Testing {feature} feature'))

                new_config = model_copy(config, deep=True)
                new_config.unsupported_features.remove(feature)

                runner = Runner(
                    database=database,
                    config=new_config,
                    for_async=for_async,
                    track_coverage=coverage,
                )

                with raises_command({1}) as result:
                    runner.setup()

                if result.did_raise:
                    print('Test setup failed (expectedly); Skipping pytest & pyright checks')
                    continue

                with raises_command({1}):
                    runner.test(pytest_args=pytest_args)

                with raises_command({1}):
                    runner.lint()

            click.echo(
                click.style(
                    f'✅ All tests successfully failed for {database}',
                    fg='green',
                )
            )


def _setup_test_env(session: nox.Session, *, pydantic_v2: bool, inplace: bool) -> None:
    if pydantic_v2:
        session.install('-r', '../pipelines/requirements/deps/pydantic.txt')
    else:
        session.install('pydantic==1.10.0')

    session.install('-r', 'requirements.txt')
    maybe_install_nodejs_bin(session)

    if inplace:  # pragma: no cover
        # useful for updating the generated code so that Pylance picks it up
        session.install('-U', '-e', '..')
    else:
        session.install('-U', '..')

    session.run('python', '-m', 'prisma', 'py', 'version')


class RaisesCommandResult:
    did_raise: bool

    def __init__(self) -> None:
        self.did_raise = False


# matches nox's CommandFailed exception message
COMMAND_FAILED_RE = re.compile(r'Returned code (\d+)')


@contextlib.contextmanager
def raises_command(
    allowed_exit_codes: set[int],
) -> Iterator[RaisesCommandResult]:
    """Context manager that intercepts and ignores `nox.CommandFailed` exceptions
    that are raised due to known exit codes. All other exceptions are passed through.
    """
    result = RaisesCommandResult()

    try:
        yield result
    except CommandFailed as exc:
        match = COMMAND_FAILED_RE.match(exc.reason or '')
        if match is None:
            raise RuntimeError(f'Could not extract exit code from exception {exc}') from exc

        exit_code = int(match.group(1))
        if exit_code not in allowed_exit_codes:
            raise RuntimeError(
                f'Unknown code: {exit_code}; Something may have gone wrong '
                + 'or this exit code must be added to the list of known exit codes; '
                + f'Allowed exit codes: {allowed_exit_codes}'
            ) from exc

        result.did_raise = True


class Runner:
    database: SupportedDatabase
    session: nox.Session
    config: DatabaseConfig
    cache_dir: Path
    track_coverage: bool
    for_async: bool

    def __init__(
        self,
        *,
        database: SupportedDatabase,
        track_coverage: bool,
        for_async: bool,
        config: DatabaseConfig | None = None,
    ) -> None:
        self.database = database
        self.session = session_ctx.get()
        self.for_async = for_async
        self.track_coverage = track_coverage
        self.config = config or CONFIG_MAPPING[database]
        self.cache_dir = ROOT_DIR / '.tests_cache' / 'databases' / database

    def _create_cache_dir(self) -> None:
        cache_dir = self.cache_dir
        if cache_dir.exists():  # pragma: no cover
            shutil.rmtree(cache_dir)

        cache_dir.mkdir(parents=True, exist_ok=True)

    def setup(self) -> None:
        # TODO: split up more
        print('database config: ' + model_json(self.config, indent=2))
        print('for async: ', self.for_async)

        exclude_files = self.exclude_files
        if exclude_files:
            print(f'excluding files:\n{yaml.dump(list(exclude_files))}')
        else:
            print('excluding files: []')

        self._create_cache_dir()

        # TODO: only create this if linting
        self._create_pyright_config()

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
                for_async=self.for_async,
                partial_generator=escape_path(DATABASES_DIR / 'partials.py'),
            )
        )

        # generate the client
        self.session.run(*self.python_args, 'prisma_cleanup')
        self.session.run(
            *self.python_args,
            'prisma',
            'generate',
            f'--schema={self.schema}',
        )

    def test(self, *, pytest_args: str | None) -> None:
        # ensure DB is in correct state
        self.session.run(
            *self.python_args,
            'prisma',
            'db',
            'push',
            '--force-reset',
            '--accept-data-loss',
            '--skip-generate',
            f'--schema={self.schema}',
        )

        args = []
        if pytest_args is not None:  # pragma: no cover
            args = shlex.split(pytest_args)

        # TODO: use PYTEST_ADDOPTS instead
        self.session.run(
            *self.python_args,
            'pytest',
            *args,
            *map(
                lambda i: f'--ignore={i}',
                self.exclude_files,
            ),
            env={
                'PRISMA_DATABASE': self.database,
                # TODO: this should be accessible in the core client
                'DATABASE_CONFIG': model_json(self.config),
            },
        )

    def lint(self) -> None:
        self.session.run('pyright', '-p', str(self.pyright_config.absolute()))

    def _create_pyright_config(self) -> None:
        pkg_location = os.path.relpath(get_pkg_location(session_ctx.get(), 'prisma'), DATABASES_DIR)

        pyright_config = deepcopy(PYRIGHT_CONFIG)
        pyright_config['exclude'].extend(self.exclude_files)

        # exclude the mypy plugin so that we don't have to install `mypy`, it is also
        # not dynamically generated which means it will stay the same across database providers
        pyright_config['exclude'].append(str(Path(pkg_location).joinpath('mypy.py')))

        # exclude our vendored code
        # this needs to explicitly be the package location as otherwise our `include`
        # of the package directory overrides other `exclude`s for the vendor dir
        pyright_config['exclude'].append(str(Path(pkg_location).joinpath('_vendor')))

        # add the generated client code to Pyright too
        pyright_config['include'].append(pkg_location)

        # ensure only the tests for sync / async are checked
        pyright_config['include'].append(tests_reldir(for_async=self.for_async))

        self.pyright_config.write_text(json.dumps(pyright_config, indent=2))

    @cached_property
    def python_args(self) -> list[str]:
        return shlex.split('coverage run --rcfile=../.coveragerc -m' if self.track_coverage else 'python -m')

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
            tests_relpath(path, for_async=self.for_async)
            for path in flatten([FEATURES_MAPPING[feature] for feature in self.config.unsupported_features])
        ]

        # ensure the tests for the sync client are not ran during the async tests anc vice versa
        files.append(tests_reldir(for_async=not self.for_async))

        return set(files)


def validate_databases(databases: list[str]) -> list[SupportedDatabase]:
    # Typer by default requires that `List` options be specified multiple times, e.g.
    #   `--databases=sqlite --databases=postgresql`
    #
    # I don't like this, I would much rather support this:
    #   `--databases=sqlite,postgresql`
    #
    # I couldn't quickly find an option to support this with Typer so
    # it is handled manually here.
    databases = flatten([d.split(',') for d in databases])
    return list(map(validate_database, databases))


def validate_database(database: str) -> SupportedDatabase:
    # We convert the input to lowercase so that we don't have to define
    # two separate names in the CI matrix.
    database = database.lower()
    if database not in SUPPORTED_DATABASES:  # pragma: no cover
        raise ValueError(f'Unknown database: {database}')

    return database


def tests_reldir(*, for_async: bool) -> str:
    return str((TESTS_DIR if for_async else SYNC_TESTS_DIR).relative_to(DATABASES_DIR))


def tests_relpath(path: str, *, for_async: bool) -> str:
    tests_dir = TESTS_DIR if for_async else SYNC_TESTS_DIR
    return str((tests_dir / path).relative_to(DATABASES_DIR))


def title(text: str) -> str:
    # TODO: improve formatting
    dashes = '-' * 30
    return dashes + ' ' + click.style(text, bold=True) + ' ' + dashes


def entrypoint(session: nox.Session) -> None:
    """Wrapper over `cli()` that sets a `session` context variable for easier usage."""

    def wrapper() -> None:
        session_ctx.set(session)
        cli(session.posargs)

    # copy the current context so that the session object is not leaked
    ctx = copy_context()
    return ctx.run(wrapper)
