from typing import List

import click
import pytest
from tests.utils import Runner


# TODO: doesn't look like this file is type checked by mypy


def test_no_args_outside_generation_warning(runner: Runner) -> None:
    result = runner.invoke([])
    assert result.exit_code == 1
    assert result.output == (
        'This command is only intended to be invoked internally. '
        'Please run the following instead:\n'
        'prisma <command>\n'
        'e.g.\n'
        'prisma generate\n'
    )


def test_invalid_command(runner: Runner) -> None:
    result = runner.invoke(['py', 'unknown'])
    assert 'Error: No such command \'unknown\'' in result.output


@pytest.mark.parametrize('args', [['py'], ['py', '--help']])
def test_custom_help(runner: Runner, args: List[str]) -> None:
    result = runner.invoke(args)
    assert 'Usage: prisma py' in result.output
    assert (
        'Custom command line arguments specifically for Prisma Client Python.'
        in result.output
    )


@pytest.mark.parametrize('args', [['-h'], ['--help']])
def test_outputs_custom_commands_info(runner: Runner, args: List[str]) -> None:
    result = runner.invoke(args)
    assert 'Python Commands' in result.output
    assert 'For Prisma Client Python commands see prisma py --help' in result.output
