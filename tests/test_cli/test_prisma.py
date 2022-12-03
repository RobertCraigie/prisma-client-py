from pathlib import Path

from prisma.cli import prisma
from prisma._config import Config

from ..utils import set_config


def test_package_json_in_parent_dir(tmp_path: Path) -> None:
    """The CLI can be installed successfully when there is a `package.json` file
    in a parent directory.
    """
    tmp_path.joinpath('package.json').write_text('{"name": "prisma-binaries"}')
    cache_dir = tmp_path / 'foo' / 'bar'

    with set_config(
        Config.parse(
            binary_cache_dir=cache_dir,
        )
    ):
        assert prisma.run(['-v']) == 0
