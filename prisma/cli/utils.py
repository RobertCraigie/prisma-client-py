import os
import sys
import logging
from enum import Enum
from pathlib import Path
from typing import Optional, List, Union, NoReturn, Mapping, Any, Type, overload

import click

from ..utils import module_exists
from .._types import Literal


log = logging.getLogger(__name__)


class PrismaCLI(click.MultiCommand):

    base_package = 'prisma.cli.commands'
    folder = Path(__file__).parent / 'commands'

    def list_commands(self, ctx: click.Context) -> List[str]:
        commands = []

        for path in self.folder.iterdir():
            name = path.name
            if name.startswith('_'):
                continue

            if name.endswith('.py'):
                commands.append(path.stem)
            elif is_module(path):
                commands.append(name)

        commands.sort()
        return commands

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        name = f'{self.base_package}.{cmd_name}'
        if not module_exists(name):
            # command not found
            return None

        mod = __import__(name, None, None, ['cli'])

        assert hasattr(
            mod, 'cli'
        ), f'Expected command module {name} to contain a "cli" attribute'
        assert isinstance(mod.cli, click.Command), (
            f'Expected command module attribute {name}.cli to be a {click.Command} '
            f'instance but got {type(mod.cli)} instead'
        )

        return mod.cli


class PathlibPath(click.Path):
    """A Click path argument that returns a pathlib Path, not a string"""

    def convert(  # type: ignore[override]
        self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> Path:
        return Path(super().convert(value, param, ctx))


class EnumChoice(click.Choice):
    """A Click choice argument created from an Enum

    choices are gathered from enum values, not their python keys, e.g.

    class MyEnum(str, Enum):
        foo = 'bar'

    results in click.Choice(['bar'])
    """

    def __init__(self, enum: Type[Enum]) -> None:
        self.__enum = enum
        super().__init__([item.value for item in enum.__members__.values()])

    def convert(
        self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> str:
        return str(self.__enum(super().convert(value, param, ctx)).value)


def is_module(path: Path) -> bool:
    return path.is_dir() and path.joinpath('__init__.py').exists()


def should_pipe() -> bool:
    """Return whether or not prisma output should be piped or printed directly to stdout

    This should only return True while testing internally
    """
    return os.environ.get('_PRISMA_PY_SHOULD_PIPE') == '1'


@overload
def error(message: str) -> NoReturn:
    ...


@overload
def error(message: str, exit_: Literal[True]) -> NoReturn:
    ...


@overload
def error(message: str, exit_: Literal[False]) -> None:
    ...


def error(message: str, exit_: bool = True) -> Union[None, NoReturn]:
    click.echo(click.style(message, fg='bright_red', bold=True), err=True)
    if exit_:
        sys.exit(1)
    else:
        return None


def pretty_info(mapping: Mapping[str, Any]) -> str:
    """Pretty print a mapping

    e.g {'foo': 'bar', 'hello': 1}

    foo   : bar
    hello : 1
    """
    pad = max(len(k) for k in mapping.keys())
    return '\n'.join(f'{k.ljust(pad)} : {v}' for k, v in mapping.items())
