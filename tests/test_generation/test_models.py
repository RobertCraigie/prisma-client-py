from pathlib import Path

import pytest
from pydantic import ValidationError
from prisma.generator.models import Module, Config


def test_module_serialization() -> None:
    """Python module serialization to json"""
    path = Path(__file__).parent.parent.joinpath(
        'scripts/partial_type_generator.py'
    )
    module = Module.parse_obj({'spec': str(path)})
    assert Module.parse_raw(module.json()).spec.name == module.spec.name


def test_recursive_type_depth() -> None:
    """Recursive type depth option disallows values that are less than 2 and do not equal -1."""
    for value in [-2, -3, 0, 1]:
        with pytest.raises(ValidationError) as exc:
            Config(recursive_type_depth=value)

        assert exc.match('Value must equal -1 or be greater than 1.')

    with pytest.raises(ValidationError) as exc:
        Config(
            recursive_type_depth='a'  # pyright: ignore[reportGeneralTypeIssues]
        )

    assert exc.match('value is not a valid integer')

    for value in [-1, 2, 3, 10, 99]:
        config = Config(recursive_type_depth=value)
        assert config.recursive_type_depth == value


def test_default_recursive_type_depth(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Warn when recursive type depth is not set:

    https://github.com/RobertCraigie/prisma-client-py/issues/252

    Ensure that we provide advice on what value to use.
    Also ensure that it defaults to 5.
    """
    c = Config()
    captured = capsys.readouterr()
    assert 'it is highly recommended to use Pyright' in captured.out.replace(
        '\n', ' '
    )
    assert c.recursive_type_depth == 5
