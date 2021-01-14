import os
import sys
import subprocess

import pytest


@pytest.fixture
def tmpdir(tmpdir):
    def generate(schema, options):
        schema_path = tmpdir.join('prisma.schema')
        schema_path.write(schema.format(output=tmpdir, options=options))
        subprocess.run(
            ['python', '-m', 'prisma', 'generate', f'--schema={schema_path}'],
            check=True,
            env=os.environ,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    tmpdir.generate = generate

    cwd = os.getcwd()
    os.chdir(tmpdir)
    sys.modules.pop('models', None)

    yield tmpdir

    sys.modules.pop('models', None)
    os.chdir(cwd)
