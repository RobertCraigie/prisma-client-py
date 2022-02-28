import re
import subprocess

import pytest

from prisma.utils import temp_env_update
from ..utils import Testdir


def _remove_coverage_warnings(output: str) -> str:
    # as we run generation under coverage we need to remove any warnings
    # for example, coverage.py will warn that the tests module was not imported
    output = re.sub(
        r'.* prisma:GeneratorProcess .* CoverageWarning:.*', '', output
    )
    output = re.sub(
        r'.* prisma:GeneratorProcess .* was never imported.*', '', output
    )
    return output


def assert_no_generator_output(output: str) -> None:
    assert 'prisma:GeneratorProcess' not in _remove_coverage_warnings(output)


def test_field_name_basemodel_attribute(testdir: Testdir) -> None:
    """Field name shadowing a basemodel attribute is not allowed"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model User {{
            id   String @id
            json String
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Field name "json" shadows a BaseModel attribute; '
        'use a different field name with \'@map("json")\''
        in str(exc.value.output, 'utf-8')
    )


def test_field_name_python_keyword(testdir: Testdir) -> None:
    """Field name shadowing a python keyword is not allowed"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model User {{
            id   String @id
            from String
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Field name "from" shadows a Python keyword; use a different field name with \'@map("from")\''
        in str(exc.value.output, 'utf-8')
    )


def test_field_name_prisma_not_allowed(testdir: Testdir) -> None:
    """Field name "prisma" is not allowed as it overrides our own method"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model User {{
            id     String @id
            prisma String
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Field name "prisma" shadows a Prisma Client Python method; '
        'use a different field name with \'@map("prisma")\''
    ) in str(exc.value.output, 'utf-8')


def test_field_name_matching_query_builder_alias_not_allowed(
    testdir: Testdir,
) -> None:
    """A field name that is the same as an alias used by our internal query builder
    is not allowed as it will lead to confusing error messages

    https://github.com/RobertCraigie/prisma-client-py/issues/124
    """
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model User {{
            id       String @id
            order_by String
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Field name "order_by" shadows an internal keyword; '
        'use a different field name with \'@map("order_by")\''
    ) in str(exc.value.output, 'utf-8')


def test_unknown_type(testdir: Testdir) -> None:
    """Unsupported scalar type is not allowed"""
    # TODO: will have to remove this test eventually
    schema = """
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
            meta Decimal
        }}
    """
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert 'Unsupported scalar field type: Decimal' in str(
        exc.value.output, 'utf-8'
    )


def test_native_binary_target_no_warning(testdir: Testdir) -> None:
    """binaryTargets only being native does not raise warning"""
    with temp_env_update({'PRISMA_PY_DEBUG': '0'}):
        result = testdir.generate(options='binaryTargets = ["native"]')

    stdout = _remove_coverage_warnings(result.stdout.decode('utf-8'))
    assert 'Warning' not in stdout
    assert 'binaryTargets option' not in stdout
    assert_no_generator_output(stdout)


def test_binary_targets_warning(testdir: Testdir) -> None:
    """Binary targets option being present raises a warning"""
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


@pytest.mark.parametrize(
    'http,new',
    [
        ('aiohttp', 'asyncio'),
        ('requests', 'sync'),
    ],
)
def test_old_http_option(testdir: Testdir, http: str, new: str) -> None:
    """A helpful error is raised if the old http config option is used"""
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(options=f'http = "{http}"')

    stdout = exc.value.stdout.decode('utf-8')
    assert (
        'The http option has been removed '
        'in favour of the interface option.' in stdout
    )
    assert (
        'Please remove the http option from '
        'your Prisma schema and replace it with:' in stdout
    )
    assert f'interface = "{new}"' in stdout


def test_compound_id_implicit_field_shaddowing(testdir: Testdir) -> None:
    """Compound IDs cannot implicitly have the same name as an already defined field

    https://github.com/prisma/prisma/issues/10456
    """
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model User {{
            name         String
            surname      String
            name_surname String

            @@id([name, surname])
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Compound constraint with name: name_surname is already used as a name for a field; '
        'Please choose a different name. For example: \n'
        '  @@id([name, surname], name: "my_custom_primary_key")'
    ) in str(exc.value.output, 'utf-8')


def test_compound_unique_constraint_implicit_field_shaddowing(
    testdir: Testdir,
) -> None:
    """Compound unique constraints cannot implicitly have the same name as an already defined field

    https://github.com/prisma/prisma/issues/10456
    """
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model User {{
            name         String
            surname      String
            name_surname String

            @@unique([name, surname])
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Compound constraint with name: name_surname is already used as a name for a field; '
        'Please choose a different name. For example: \n'
        '  @@unique([name, surname], name: "my_custom_primary_key")'
    ) in str(exc.value.output, 'utf-8')
