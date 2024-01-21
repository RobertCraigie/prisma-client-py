from pathlib import Path

from click.testing import Result

from prisma import config
from prisma._config import Config

from ..utils import Runner, set_config


def assert_success(result: Result) -> None:
    assert result.exit_code == 0
    assert result.output.endswith(f'Downloaded binaries to {config.binary_cache_dir}\n')


def test_fetch(runner: Runner) -> None:
    """Basic usage, binaries are already cached"""
    assert_success(runner.invoke(['py', 'fetch']))


def test_fetch_not_cached(runner: Runner, tmp_path: Path) -> None:
    """Basic usage, binaries are not cached"""
    with set_config(Config.parse(binary_cache_dir=tmp_path)):
        assert_success(runner.invoke(['py', 'fetch']))
