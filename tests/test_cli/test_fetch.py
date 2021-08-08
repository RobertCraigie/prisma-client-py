import random
import shutil

from click.testing import Result

from prisma import binaries
from tests.utils import Runner


# TODO: this could probably mess up other tests if one of these
# tests fails mid run, as the global binaries are deleted


def assert_success(result: Result) -> None:
    assert result.exit_code == 0
    assert result.output.endswith(
        f'Downloaded binaries to {binaries.GLOBAL_TEMP_DIR}\n'
    )

    for binary in binaries.BINARIES:
        assert binary.path.exists()


def test_fetch(runner: Runner) -> None:
    assert_success(runner.invoke(['py', 'fetch']))


def test_fetch_one_binary_missing(runner: Runner) -> None:
    binary = random.choice(binaries.BINARIES)
    assert binary.path.exists()
    binary.path.unlink()
    assert not binary.path.exists()

    assert_success(runner.invoke(['py', 'fetch']))


def test_fetch_force(runner: Runner) -> None:
    binary = random.choice(binaries.BINARIES)
    assert binary.path.exists()
    old_stat = binary.path.stat()

    assert_success(runner.invoke(['py', 'fetch', '--force']))

    new_stat = binary.path.stat()

    # file identification number, difference proves deletion and creation
    assert old_stat.st_ino != new_stat.st_ino

    # modified time
    assert old_stat.st_mtime_ns != new_stat.st_mtime_ns

    # ensure downloaded the same as before
    assert old_stat.st_size == new_stat.st_size


def test_fetch_force_no_dir(runner: Runner) -> None:
    binaries.remove_all()
    shutil.rmtree(str(binaries.GLOBAL_TEMP_DIR))

    binary = binaries.BINARIES[0]
    assert not binary.path.exists()

    assert_success(runner.invoke(['py', 'fetch', '--force']))
