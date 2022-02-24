import sys
import pkgutil
import subprocess
from typing import TYPE_CHECKING

import pytest
from prisma_cleanup import cleanup
from prisma.generator import BASE_PACKAGE_DIR
from prisma.generator.utils import copy_tree

from .utils import assert_module_is_clean, assert_module_not_clean
from ..utils import Testdir

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


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


def test_unresolvable_loader(
    monkeypatch: 'MonkeyPatch', capsys: 'CaptureFixture[str]'
) -> None:
    """pkgutil.get_loader() can return a loader that doesn't have access to
    the packages source location.
    """

    def patched_get_loader(pkg: str) -> object:
        return 'Dummy'

    monkeypatch.setattr(pkgutil, 'get_loader', patched_get_loader)

    with pytest.raises(SystemExit) as exc:
        cleanup()  # type: ignore

    captured = capsys.readouterr()
    assert exc.value.code == 1
    assert captured.out == 'Received unresolvable import loader: Dummy\n'
