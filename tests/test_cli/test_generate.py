import json
from enum import Enum
from typing import (
    Any,
    Dict,
    Type,
    Tuple,
    Callable,
    Iterator,
    Optional,
    Generator,
)
from pathlib import Path
from itertools import chain

import pytest
import pydantic
from _pytest.monkeypatch import MonkeyPatch

from prisma.utils import temp_env_update
from prisma.generator.models import InterfaceChoices

from ..utils import Runner, Testdir

# all these tests simply ensure the correct config is being parsed by generator.run,
# as each config option is individually tested elsewwere we can be sure that each
# config option results in the intended output

# TODO: test watch option
# TODO: nearly all of these tests could be optimised by exiting the generator early
# and not actually generating the client as we don't make use of it in any of these tests


@pytest.fixture(autouse=True)
def setup_env() -> Iterator[None]:
    with temp_env_update({'PRISMA_PY_DEBUG_GENERATOR': '1'}):
        yield


def run_test(
    runner: Runner,
    testdir: Testdir,
    argument: Optional[str],
    options: Optional[str],
    do_assert: Callable[[Dict[str, Any]], None],
) -> None:
    if options is None:
        options = ''

    schema = testdir.make_schema(options=options)

    args = ['py', 'generate', f'--schema={schema}']
    if argument is not None:
        args.append(argument)

    result = runner.invoke(args)
    print(result.output)
    assert result.exit_code == 0

    path = testdir.path / 'prisma' / 'generator' / 'debug-data.json'
    data = json.loads(path.read_text())
    do_assert(data)


def from_enum(enum: Type[Enum], arg: str) -> Generator[Tuple[str, str, None], None, None]:
    return ((item.value, arg + item.value, None) for item in enum.__members__.values())


def test_unsupported_pydantic_version(runner: Runner, monkeypatch: MonkeyPatch) -> None:
    """Using an older version of pydantic outputs warning

    We need to use pydantic>=1.8.2 as that added the customise_sources config option to
    prioritise env variables over init kwargs.
    """
    monkeypatch.setattr(pydantic, 'VERSION', '1.6.2', raising=True)
    result = runner.invoke(['py', 'generate'])
    assert result.output.startswith(
        'WARNING: Unsupported version of pydantic installed, this command may not work as intended\n'
        'Please update pydantic to 1.8 or greater'
    )


def test_bad_interface_option(runner: Runner) -> None:
    """Passing an unknown interface option raises an error"""
    result = runner.invoke(['py', 'generate', '--interface=foo'])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--interface'" in result.output
    assert 'foo' in result.output
    assert 'sync' in result.output
    assert 'asyncio' in result.output


def test_prisma_error_non_zero_exit_code(testdir: Testdir, runner: Runner) -> None:
    """Exits non-zero when the prisma process exits non-zero"""
    path = testdir.make_schema(schema=testdir.default_schema + 'foo')
    result = runner.invoke(['py', 'generate', f'--schema={path}'])
    assert result.exit_code != 0
    assert 'Error code: P1012' in result.output


def test_schema_not_found(runner: Runner) -> None:
    """Passing non-existent schema raises an error"""
    result = runner.invoke(['py', 'generate', '--schema=foo'])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--schema': File 'foo' does not exist." in result.output


@pytest.mark.parametrize(
    'target,argument,options',
    chain(
        from_enum(InterfaceChoices, '--interface='),
        [
            ('sync', None, 'interface = sync'),  # ensure uses schema property
            # ensure overrides
            ('asyncio', '--interface=asyncio', 'interface = sync'),
        ],
    ),
)
def test_interface_option(
    testdir: Testdir,
    runner: Runner,
    target: str,
    argument: Optional[str],
    options: Optional[str],
) -> None:
    """interface option is overrided correctly"""

    def do_assert(data: Dict[str, Any]) -> None:
        assert data['generator']['config']['interface'] == target

    run_test(runner, testdir, argument, options, do_assert)


@pytest.mark.parametrize(
    'target,argument,options',
    [
        (None, None, None),  # default
        ('partials.py', '--partials=partials.py', None),
        ('partials.py', None, 'partial_type_generator = "partials.py"'),
        (
            'partials.py',
            '--partials=partials.py',
            'partial_type_generator = "invalid.py"',
        ),
    ],
)
def test_partials_option(
    testdir: Testdir,
    runner: Runner,
    target: Optional[str],
    argument: Optional[str],
    options: Optional[str],
) -> None:
    """partial type generator option is overrided correctly"""

    def do_assert(data: Dict[str, Any]) -> None:
        partial_type_generator = data['generator']['config']['partial_type_generator']
        if target is None:
            assert partial_type_generator is None
        else:
            actual = Path(partial_type_generator['spec']).absolute()
            assert actual == Path(target).absolute()

    def partials() -> None:  # mark: filedef
        pass

    testdir.make_from_function(partials, name='partials.py')
    run_test(runner, testdir, argument, options, do_assert)


@pytest.mark.parametrize(
    'target,argument,options',
    [
        (5, None, None),  # default
        (3, None, 'recursive_type_depth = 3'),  # ensure uses schema property
        (-1, '-t -1', 'recursive_type_depth = 3'),  # ensure overrides
    ],
)
def test_type_depth_option(
    testdir: Testdir,
    runner: Runner,
    target: str,
    argument: Optional[str],
    options: Optional[str],
) -> None:
    """recursive_type_depth option is overrided correctly"""

    def do_assert(data: Dict[str, Any]) -> None:
        assert data['generator']['config']['recursive_type_depth'] == target

    run_test(runner, testdir, argument, options, do_assert)
