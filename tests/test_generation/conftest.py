import os
from typing import Iterator

import pytest
from _pytest.pytester import Testdir as PytestTestdir

from .utils import Testdir


@pytest.fixture(name='testdir')
def testdir_fixture(testdir: PytestTestdir) -> Iterator[Testdir]:
    cwd = os.getcwd()
    os.chdir(testdir.tmpdir)

    yield Testdir(testdir)

    os.chdir(cwd)
