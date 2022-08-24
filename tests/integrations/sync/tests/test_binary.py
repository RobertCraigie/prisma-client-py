import os
import random
import pytest
from prisma.binaries import BINARIES


@pytest.mark.skip_if_custom_binaries
def test_download() -> None:
    """Binary can be downloaded"""

    binary = random.choice(BINARIES)
    assert binary.path.exists()
    binary.path.unlink()
    assert not binary.path.exists()

    binary.download()

    assert binary.path.exists()
