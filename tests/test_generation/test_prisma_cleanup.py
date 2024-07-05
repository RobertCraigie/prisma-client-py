import sys
import subprocess

import pytest
from prisma_cleanup import cleanup

from prisma.generator import BASE_PACKAGE_DIR
from prisma.generator.utils import copy_tree

from .utils import assert_module_is_clean, assert_module_not_clean
from ..utils import Testdir


def test_main(testdir: Testdir) -> None:
    """Main entrypoint"""
    path = testdir.path / 'prisma'
    assert not path.exists()
    copy_tree(BASE_PACKAGE_DIR, path)

    assert_module_not_clean(path)
    subprocess.run(
        [sys.executable, '-m', 'prisma_cleanup'],
        check=True,
        stdout=subprocess.PIPE,
    )
    assert_module_is_clean(path)


def test_main_works_with_erroneous_client(testdir: Testdir) -> None:
    """The main entrypoint works regardless of any errors in the prisma/client.py file"""
    path = testdir.path / 'prisma'
    assert not path.exists()
    copy_tree(BASE_PACKAGE_DIR, path)
    (path / 'client.py').write_text('raise RuntimeError("Hello, there!")')

    # ensure importing would fail
    with pytest.raises(subprocess.CalledProcessError) as exc:
        subprocess.run(
            ['python', '-c', 'import prisma'],
            check=True,
            stderr=subprocess.PIPE,
        )

    assert 'Hello, there!' in exc.value.stderr.decode('utf-8')

    # ensure cleanup works
    assert_module_not_clean(path)
    subprocess.run(
        [sys.executable, '-m', 'prisma_cleanup'],
        check=True,
        stdout=subprocess.PIPE,
    )
    assert_module_is_clean(path)


def test_custom_package(testdir: Testdir) -> None:
    """Cleaning up custom package location"""
    path = testdir.path / 'app' / 'prisma'
    assert not path.exists()
    copy_tree(BASE_PACKAGE_DIR, path)

    assert_module_not_clean(path)
    subprocess.run(
        [sys.executable, '-m', 'prisma_cleanup', 'app.prisma'],
        check=True,
        stdout=subprocess.PIPE,
    )
    assert_module_is_clean(path)


def test_cleanup_non_prisma_package(testdir: Testdir) -> None:
    """Cleaning up a non Prisma package does not work"""
    path = testdir.path / 'prisma_custom' / '__init__.py'
    path.parent.mkdir()
    path.touch()

    with pytest.raises(RuntimeError) as exc:
        cleanup('prisma_custom')

    assert exc.value.args[0] == 'The given package does not appear to be a Prisma Client Python package.'


def test_cleanup_package_not_found(testdir: Testdir) -> None:
    """Cleaning up a non-existent package does not work"""
    with pytest.raises(RuntimeError) as exc:
        cleanup('prisma_custom')

    assert exc.value.args[0] == 'Could not resolve package: prisma_custom'
