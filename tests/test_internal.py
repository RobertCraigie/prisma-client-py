import os
import filecmp
from pathlib import Path

from prisma.generator.utils import copy_tree

from pipelines.generator import generate_all


DATABASES_PATH = Path(__file__).parent.parent / 'databases'


# TODO: add tests that the templates are all included


def test_databases(tmp_path: Path) -> None:
    """Ensure the auto-generated database tests are up to date"""
    raise RuntimeError('TODO')
