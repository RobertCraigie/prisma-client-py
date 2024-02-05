from prisma.generator.utils import copy_tree, to_camel_case, to_pascal_case, to_snake_case

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


def test_to_snake_case() -> None:
    snake_case = 'snake_case_test'
    pascal_case = 'PascalCaseTest'
    camel_case = 'camelCaseTest'
    # TODO: implement mixed case
    # mixed_case = "Mixed_Case_Test" # mixed case is not supported

    assert to_snake_case(snake_case) == 'snake_case_test'
    assert to_snake_case(pascal_case) == 'pascal_case_test'
    assert to_snake_case(camel_case) == 'camel_case_test'
    # assert to_snake_case(mixed_case) == "mixed_case_test" # output: mixed__case__test


def test_to_pascal_case() -> None:
    snake_case = 'snake_case_test'
    pascal_case = 'PascalCaseTest'
    camel_case = 'camelCaseTest'
    mixed_case = 'Mixed_Case_Test'

    assert to_pascal_case(snake_case) == 'SnakeCaseTest'
    assert to_pascal_case(pascal_case) == 'PascalCaseTest'
    assert to_pascal_case(camel_case) == 'CamelCaseTest'
    assert to_pascal_case(mixed_case) == 'MixedCaseTest'


def test_to_camel_case() -> None:
    snake_case = 'snake_case_test'
    pascal_case = 'PascalCaseTest'
    camel_case = 'camelCaseTest'
    mixed_case = 'Mixed_Case_Test'

    assert to_camel_case(snake_case) == 'snakeCaseTest'
    assert to_camel_case(pascal_case) == 'pascalCaseTest'
    assert to_camel_case(camel_case) == 'camelCaseTest'
    assert to_camel_case(mixed_case) == 'mixedCaseTest'
