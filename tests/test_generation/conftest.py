import os
import sys
from typing import Iterator

import py
import pytest

from .utils import Tmpdir


@pytest.fixture(name='tmpdir')
def tmpdir_fixture(tmpdir: py.path.local) -> Iterator[Tmpdir]:
    cwd = os.getcwd()
    os.chdir(tmpdir)
    sys.modules.pop('models', None)

    yield Tmpdir(tmpdir)

    sys.modules.pop('models', None)
    os.chdir(cwd)
