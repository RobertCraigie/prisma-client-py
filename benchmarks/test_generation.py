import os
import sys
import subprocess
from pathlib import Path

import pytest


THIS_DIR = Path(__file__).parent
SCHEMAS_DIR = THIS_DIR / 'schemas'

SCHEMAS = list(SCHEMAS_DIR.glob('*.prisma'))


@pytest.mark.benchmark
@pytest.mark.parametrize(
    'schema',
    SCHEMAS,
    ids=[schema.name for schema in SCHEMAS],
)
def test_client_generation(tmp_path: Path, schema: Path) -> None:
    """Benchmarks for how long client generation takes in different circumstances"""
    subprocess.check_call(
        [
            sys.executable,
            '-m',
            'prisma',
            'generate',
            f'--schema={schema.absolute()}',
        ],
        env={
            **os.environ,
            'PRISMA_OUTPUT': str(tmp_path / 'generated'),
            'PRISMA_USE_GLOBAL_NODE': '0',
            'PRISMA_USE_NODEJS_BIN': '1',
        },
    )
