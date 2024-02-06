from pathlib import Path

import pytest
from pydantic import ValidationError

from prisma._compat import (
    PYDANTIC_V2,
    model_json,
    model_parse,
    model_parse_json,
)
from prisma.generator.models import Config, Module


def test_module_serialization() -> None:
    """Python module serialization to json"""
    path = Path(__file__).parent.parent.joinpath('scripts/partial_type_generator.py')
    module = model_parse(Module, {'spec': str(path)})
    assert model_parse_json(Module, model_json(module)).spec.name == module.spec.name


def test_recursive_type_depth() -> None:
    """Recursive type depth option disallows values that are less than 2 and do not equal -1."""
    for value in [-2, -3, 0, 1]:
        with pytest.raises(ValidationError) as exc:
            Config(recursive_type_depth=value)

        assert exc.match('Value must equal -1 or be greater than 1.')

    with pytest.raises(ValidationError) as exc:
        Config(
            recursive_type_depth='a'  # pyright: ignore[reportArgumentType]
        )

    if PYDANTIC_V2:
        assert exc.match('Input should be a valid integer, unable to parse string as an integer')
    else:
        assert exc.match('value is not a valid integer')

    for value in [-1, 2, 3, 10, 99]:
        config = Config(recursive_type_depth=value)
        assert config.recursive_type_depth == value


def test_default_recursive_type_depth(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Warn when recursive type depth is not set:

    https://github.com/RobertCraigie/prisma-client-py/issues/252

    Ensure that we provide advice on what value to use and that it defaults to 5.

    Also validate that when a type depth is provided, no warning is shown.
    """
    c = Config()
    captured = capsys.readouterr()
    assert 'it is highly recommended to use Pyright' in captured.out.replace('\n', ' ')
    assert c.recursive_type_depth == 5

    c = Config(recursive_type_depth=5)
    captured = capsys.readouterr()
    assert 'it is highly recommended to use Pyright' not in captured.out.replace('\n', ' ')
    assert c.recursive_type_depth == 5

    c = Config(recursive_type_depth=2)
    captured = capsys.readouterr()
    assert 'it is highly recommended to use Pyright' not in captured.out.replace('\n', ' ')
    assert c.recursive_type_depth == 2
