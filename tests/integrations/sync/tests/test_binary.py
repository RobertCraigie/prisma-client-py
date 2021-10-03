import random
from prisma.binaries import BINARIES


def test_download() -> None:
    """Binary can be downloaded"""
    binary = random.choice(BINARIES)
    assert binary.path.exists()
    binary.path.unlink()
    assert not binary.path.exists()

    binary.download()

    assert binary.path.exists()
