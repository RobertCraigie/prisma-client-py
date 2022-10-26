import pathlib
from pytest_mock import MockerFixture

from prisma.binaries.binaries import PRISMA_FORMAT_BINARY


def test_download(
    mocker: MockerFixture,
    tmp_path: pathlib.Path,
) -> None:
    """Binary can be downloaded"""
    # Always use the format engine binary since its quite small relative
    # to other binaries.
    # NOTE: unlike the test_fetch tetsts, this is not mocked and will
    # make the network transfer. We do it in a separate directory so
    # as to not create issues for other tests if we start parallelizing
    mocker.patch('prisma.config.binary_cache_dir', tmp_path)

    binary = PRISMA_FORMAT_BINARY
    assert not binary.path.exists()
    binary.download()

    assert binary.path.exists()
