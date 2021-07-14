import os
import sys
import subprocess
import contextlib
from pathlib import Path
from typing import Iterator

import click


# TODO: we should use pytest for running integration tests directly


ROOT = (Path(__file__).parent.parent / 'integrations').absolute()


@click.group()
def cli() -> None:
    """Scripts for integration tests"""


@cli.command()
def run() -> None:
    """Run integration tests"""
    for integration in ROOT.iterdir():
        click.echo(
            f'Starting {click.style(integration.name, bold=True)} integration test\n'
        )

        with chdir(integration):
            setup = integration / 'setup.py'
            if setup.exists():
                step('setup.py')
                exec_file(setup)

            runner = integration / 'run.py'
            assert (
                runner.exists()
            ), f'Integration test: {integration.name} doesn\'t contain a run.py file'
            step('run.py')
            exec_file(runner)


@contextlib.contextmanager
def chdir(path: Path) -> Iterator[Path]:
    cwd = os.getcwd()
    os.chdir(str(path))

    yield path

    os.chdir(cwd)


def exec_file(script: Path) -> None:
    # TODO: add option to not exit, we should be able to run all integration tests
    proc = subprocess.run([sys.executable, str(script)])
    if proc.returncode != 0:
        sys.exit(proc.returncode)


def step(thing: str) -> None:
    click.echo('Invoking ' + click.style(thing, bold=True))
    click.echo(click.style('=' * len('Invoking ' + thing), bold=True))


if __name__ == '__main__':
    cli()
