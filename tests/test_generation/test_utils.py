import pytest

from prisma.generator.utils import (
    copy_tree,
    to_camel_case,
    to_snake_case,
    to_pascal_case,
    to_constant_case,
)

from ..utils import Testdir


def test_copy_tree_ignores_files(testdir: Testdir) -> None:
    """Ensure *.pyc and __pycache__ files are not copied"""
    p1 = testdir.path / 'p1'
    p1.mkdir()
    p1.joinpath('foo.pyc').touch()
    p1.joinpath('foo.py').touch()
    p1.joinpath('bar.py').touch()
    p1.joinpath('__pycache__').mkdir()
    p1.joinpath('__pycache__/hello.py').touch()
    assert len(list(p1.glob('**/*'))) == 5

    p2 = testdir.path / 'p2'
    p2.mkdir()
    p2.joinpath('hello.py').touch()
    assert len(list(p2.glob('**/*'))) == 1

    copy_tree(p1, p2)

    files = sorted(list(p2.glob('**/*')))
    assert len(files) == 3
    assert files[0].name == 'bar.py'
    assert files[1].name == 'foo.py'
    assert files[2].name == 'hello.py'


@pytest.mark.parametrize(
    'input_str,expected',
    [
        ('snake_case_test', 'snake_case_test'),
        ('PascalCaseTest', 'pascal_case_test'),
        ('camelCaseTest', 'camel_case_test'),
        ('Mixed_Case_Test', 'mixed_case_test'),
    ],
)
def test_to_snake_case(input_str: str, expected: str) -> None:
    assert to_snake_case(input_str) == expected


@pytest.mark.parametrize(
    'input_str,expected',
    [
        ('snake_case_test', 'SnakeCaseTest'),
        ('PascalCaseTest', 'PascalCaseTest'),
        ('camelCaseTest', 'CamelCaseTest'),
        ('Mixed_Case_Test', 'MixedCaseTest'),
    ],
)
def test_to_pascal_case(input_str: str, expected: str) -> None:
    assert to_pascal_case(input_str) == expected


@pytest.mark.parametrize(
    'input_str,expected',
    [
        ('snake_case_test', 'snakeCaseTest'),
        ('PascalCaseTest', 'pascalCaseTest'),
        ('camelCaseTest', 'camelCaseTest'),
        ('Mixed_Case_Test', 'mixedCaseTest'),
    ],
)
def test_to_camel_case(input_str: str, expected: str) -> None:
    assert to_camel_case(input_str) == expected


@pytest.mark.parametrize(
    'input_str,expected',
    [
        ('snake_case_test', 'SNAKE_CASE_TEST'),
        ('PascalCaseTest', 'PASCAL_CASE_TEST'),
        ('camelCaseTest', 'CAMEL_CASE_TEST'),
        ('Mixed_Case_Test', 'MIXED_CASE_TEST'),
    ],
)
def test_to_constant_case(input_str: str, expected: str) -> None:
    assert to_constant_case(input_str) == expected
