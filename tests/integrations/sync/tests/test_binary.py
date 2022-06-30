import os
import random
import pytest
from prisma.binaries import BINARIES


def test_download() -> None:
    """Binary can be downloaded"""

    if os.environ.get('PRISMA_CUSTOM_BINARIES'):
        pytest.skip('unsupported configuration')

    binary = random.choice(BINARIES)
    assert binary.path.exists()
    binary.path.unlink()
    assert not binary.path.exists()

    binary.download()

    assert binary.path.exists()
