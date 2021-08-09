import re
import subprocess

import pytest

from prisma.utils import temp_env_update
from ..utils import Testdir


def assert_no_generator_output(output: str) -> None:
    # as we run generation under coverage we need to remove any warnings
    # for example, coverage.py will warn that the tests module was not imported
    output = re.sub(r'.* prisma:GeneratorProcess Coverage.py warning:.*', '', output)
    assert 'prisma:GeneratorProcess' not in output


def test_field_name_basemodel_attribute(testdir: Testdir) -> None:
    schema = (
        testdir.SCHEMA_HEADER
        + '''
        model User {{
            id   String @id
            json String
        }}
    '''
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Field name "json" shadows a BaseModel attribute; '
        'use a different field name with \'@map("json")\''
        in str(exc.value.output, 'utf-8')
    )


def test_field_name_python_keyword(testdir: Testdir) -> None:
    schema = (
        testdir.SCHEMA_HEADER
        + '''
        model User {{
            id   String @id
            from String
        }}
    '''
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Field name "from" shadows a Python keyword; use a different field name with \'@map("from")\''
        in str(exc.value.output, 'utf-8')
    )


def test_unknown_type(testdir: Testdir) -> None:
    schema = '''
        datasource db {{
          provider = "postgres"
          url      = env("POSTGRES_URL")
        }}

        generator db {{
          provider = "coverage run -m prisma"
          output = "{output}"
          {options}
        }}

        model User {{
            id   String @id
            meta Json
        }}
    '''
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert 'Unknown scalar type: Json' in str(exc.value.output, 'utf-8')


def test_native_binary_target_no_warning(testdir: Testdir) -> None:
    with temp_env_update({'PRISMA_PY_DEBUG': '0'}):
        result = testdir.generate(options='binaryTargets = ["native"]')

    stdout = result.stdout.decode('utf-8')
    assert 'Warning' not in stdout
    assert 'binaryTargets option' not in stdout
    assert_no_generator_output(stdout)


def test_binary_targets_warning(testdir: Testdir) -> None:
    with temp_env_update({'PRISMA_PY_DEBUG': '0'}):
        result = testdir.generate(
            options='binaryTargets = ["native", "rhel-openssl-1.1.x"]'
        )

    stdout = result.stdout.decode('utf-8')
    assert_no_generator_output(stdout)
    assert (
        'Warning: The binaryTargets option '
        'is not currently supported by Prisma Client Python' in stdout
    )
