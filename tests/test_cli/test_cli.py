from enum import Enum
from typing import List

import click
import pytest

from tests.utils import Runner
from prisma.cli.utils import EnumChoice

# TODO: doesn't look like this file is type checked by mypy


def test_no_args_outside_generation_warning(runner: Runner) -> None:
    """Running just `prisma` raises an error as it should only be ran by prisma internally"""
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
    """Trying to run an unknown command errors"""
    result = runner.invoke(['py', 'unknown'])
    assert "Error: No such command 'unknown'" in result.output


@pytest.mark.parametrize('args', [['py'], ['py', '--help']])
def test_custom_help(runner: Runner, args: List[str]) -> None:
    """Correct program name is output for help message"""
    result = runner.invoke(args)
    assert 'Usage: prisma py' in result.output
    assert 'Custom command line arguments specifically for Prisma Client Python.' in result.output


@pytest.mark.parametrize('args', [['-h'], ['--help']])
def test_outputs_custom_commands_info(runner: Runner, args: List[str]) -> None:
    """Running `prisma --help` also outputs a message for our help command"""
    result = runner.invoke(args)
    assert 'Python Commands' in result.output
    assert 'For Prisma Client Python commands run prisma py --help' in result.output


def test_int_enum_choice() -> None:
    """Non-str subclassing enum cannot be used with EnumChoice"""

    class MyEnum(int, Enum):
        bob = 1
        alice = 2

    with pytest.raises(TypeError) as exc:
        EnumChoice(MyEnum)

    assert exc.match('Enum does not subclass `str`')


def test_str_enum_choice(runner: Runner) -> None:
    """EnumChoice correctly accepts and rejects arguments"""

    class MyEnum(str, Enum):
        bob = 'bob'
        alice = 'alice'

    @click.command()
    @click.option(
        '--argument',
        type=EnumChoice(MyEnum),
    )
    def cli(argument: str) -> None:
        if argument == MyEnum.bob:
            click.echo('is bob')
        elif argument == MyEnum.alice:
            click.echo('is alice')
        else:  # pragma: no cover
            # this should never happen
            raise ValueError('Unknown enum value passed.')

    result = runner.invoke(['--argument=bob'], cli=cli)
    assert result.output == 'is bob\n'

    result = runner.invoke(['--argument=alice'], cli=cli)
    assert result.output == 'is alice\n'

    result = runner.invoke(['--argument=invalid'], cli=cli)
    assert "Error: Invalid value for '--argument':" in result.output
    assert 'bob' in result.output
    assert 'alice' in result.output
    assert 'invalid' in result.output
