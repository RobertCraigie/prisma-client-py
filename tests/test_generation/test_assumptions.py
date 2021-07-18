import subprocess

import pytest
from prisma.utils import temp_env_update

from ..utils import Testdir


def test_one_datasource_allowed(testdir: Testdir) -> None:
    schema = (
        testdir.SCHEMA_HEADER
        + '''
        datasource db2 {{
          provider = "sqlite"
          url      = "file:dev-2.db"
        }}
    '''
    )

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    output = exc.value.output.decode('utf-8')
    assert (
        'You defined more than one datasource. '
        'This is not allowed yet because support for multiple databases '
        'has not been implemented yet' in output
    )


def test_can_generate_from_env_var(testdir: Testdir) -> None:
    schema = '''
    datasource db {{
      provider = "sqlite"
      url      = "file:dev.db"
    }}

    // default output: {output}
    generator db {{
      provider = "coverage run -m prisma"
      output   = env("PRISMA_TEST_ASSUMPTIONS_OUTPUT")
      {options}
    }}

    model User {{
      id    Int     @id @default(autoincrement())
      email String  @unique
      name  String?
    }}
    '''

    with temp_env_update(
        {'PRISMA_TEST_ASSUMPTIONS_OUTPUT': str(testdir.path / 'prisma')}
    ):
        testdir.generate(schema=schema)
