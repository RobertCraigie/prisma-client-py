from prisma.generator.utils import copy_tree

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
