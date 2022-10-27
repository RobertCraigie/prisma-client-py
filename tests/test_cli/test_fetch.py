import pathlib
import shutil
from mock import MagicMock
from typing import cast

from pytest_mock import MockerFixture

from click.testing import Result
from tests.utils import Runner, skipif_windows
from prisma import config
from prisma.binaries import binary, BINARIES
from prisma.binaries.binaries import PRISMA_FORMAT_BINARY

# TODO: this could probably mess up other tests if one of these
# tests fails mid run, as the global binaries are deleted

# Use a closure to capture the original value of the path -- this is from the cache
# which should have already been downloaded to by the time this test module
# got invoked
_original_binary_path = PRISMA_FORMAT_BINARY.path


def _copy_cached_binaries_to_dir(destination: pathlib.Path) -> None:
    assert _original_binary_path.exists()
    original_binaries = list(_original_binary_path.parent.glob('*'))
    assert len(original_binaries) == len(BINARIES)
    for f in original_binaries:
        shutil.copy2(f, destination)


def assert_success(result: Result, cache_dir: pathlib.Path) -> None:
    assert result.exit_code == 0
    assert result.output.endswith(f'Downloaded binaries to {str(cache_dir)}\n')


def test_fetch(runner: Runner, mocker: MockerFixture) -> None:
    """Basic usage, binaries are already cached"""
    # https://pytest-mock.readthedocs.io/en/latest/usage.html#
    download_mock = cast(
        MagicMock, mocker.patch.object(binary, 'download', autospec=True)
    )
    assert_success(runner.invoke(['py', 'fetch']), config.binary_cache_dir)
    assert (
        download_mock.call_count == 0
    ), 'Download should not have been invoked'


# it seems like we can't use `.unlink()` on binary paths on windows due to permissions errors


@skipif_windows
def test_fetch_one_binary_missing(
    runner: Runner,
    mocker: MockerFixture,
    tmp_path: pathlib.Path,
) -> None:
    """Downloads a binary if it is missing"""
    # https://pytest-mock.readthedocs.io/en/latest/usage.html#
    # monkeypatch.setenv("PRISMA_BINARY_CACHE_DIR", str(tmp_path))
    _copy_cached_binaries_to_dir(tmp_path)
    download_mock = cast(
        MagicMock, mocker.patch.object(binary, 'download', autospec=True)
    )
    mocker.patch('prisma.config.binary_cache_dir', tmp_path)

    original_contents = list(tmp_path.glob('*'))
    original_contents[0].unlink()
    contents_after = list(tmp_path.glob('*'))
    assert len(contents_after) == (len(original_contents) - 1)

    assert_success(runner.invoke(['py', 'fetch']), tmp_path)
    assert (
        download_mock.call_count == 1
    ), f'Exepected download to have been called for a single binary'


@skipif_windows
def test_fetch_force(
    runner: Runner, mocker: MockerFixture, tmp_path: pathlib.Path
) -> None:
    """Passing --force re-downloads an already existing binary"""
    mocker.patch('prisma.config.binary_cache_dir', tmp_path)
    assert not PRISMA_FORMAT_BINARY.path.exists()
    _copy_cached_binaries_to_dir(tmp_path)
    assert PRISMA_FORMAT_BINARY.path.exists()

    download_mock = cast(
        MagicMock, mocker.patch.object(binary, 'download', autospec=True)
    )
    assert_success(runner.invoke(['py', 'fetch', '--force']), tmp_path)
    assert download_mock.call_count == len(
        BINARIES
    ), f'Exepected download to have been called for each engine {BINARIES}'


@skipif_windows
def test_fetch_force_no_dir(
    runner: Runner, mocker: MockerFixture, tmp_path: pathlib.Path
) -> None:
    """Passing --force when the base directory does not exist"""
    assert tmp_path.exists()
    mocker.patch('prisma.config.binary_cache_dir', tmp_path)
    tmp_path.rmdir()
    assert not tmp_path.exists()
    download_mock = cast(
        MagicMock, mocker.patch.object(binary, 'download', autospec=True)
    )
    assert_success(runner.invoke(['py', 'fetch', '--force']), tmp_path)
    assert download_mock.call_count == len(
        BINARIES
    ), f'Exepected download to have been called for each engine {BINARIES}'
