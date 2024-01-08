from pathlib import Path

import click
import pytest

from prisma.cli import utils
from tests.utils import Runner


class PrismaCLI(utils.PrismaCLI):
    base_package = 'tests.test_cli.commands'
    folder = Path(__file__).parent / 'commands'


@pytest.fixture
def ctx(cli: PrismaCLI) -> click.Context:
    return cli.make_context('prisma py', ['example'])


@pytest.fixture
def cli() -> PrismaCLI:
    return PrismaCLI()


@pytest.fixture
def runner(runner: Runner, cli: PrismaCLI) -> Runner:
    runner.default_cli = cli
    return runner


def test_missing_cli_attr(runner: Runner) -> None:
    """Loading command that does not have a cli attribute raises an error"""
    result = runner.invoke(['missing_cli_attr'])
    assert isinstance(result.exception, AssertionError)
    assert str(result.exception) == (
        'Expected command module tests.test_cli.commands.missing_cli_attr ' 'to contain a "cli" attribute'
    )


def test_wrong_cli_type(runner: Runner) -> None:
    """Loading command with a cli attribute that is not a click command raises an error"""
    result = runner.invoke(['wrong_cli_type'])
    assert isinstance(result.exception, AssertionError)
    assert str(result.exception) == (
        'Expected command module attribute tests.test_cli.commands.wrong_cli_type.cli '
        "to be a <class 'click.core.Command'> instance but got <class 'function'> "
        'instead'
    )


def test_example_command(runner: Runner) -> None:
    """Basic correctly implemented command"""
    result = runner.invoke(['example'])
    assert result.output == 'Hello from example command!\n'
    assert result.exit_code == 0


def test_list_commands(cli: PrismaCLI, ctx: click.Context) -> None:
    """List commands ignores private modules"""
    commands = cli.list_commands(ctx)
    assert 'foo' in commands
    assert 'example' in commands
    assert '_private' not in commands
