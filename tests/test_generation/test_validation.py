import re
import subprocess

import pytest

from prisma.utils import temp_env_update

from ..utils import Testdir


def _remove_known_warnings(output: str) -> str:
    # as we run generation under coverage we need to remove any warnings
    # for example, coverage.py will warn that the tests module was not imported
    output = re.sub(r'.*prisma:GeneratorProcess .* CoverageWarning:.*', '', output)
    output = re.sub(r'.*prisma:GeneratorProcess .* was never imported.*', '', output)

    # unknown why this is logged but it doesn't seem to effect anything
    output = re.sub(
        r'.*prisma:GeneratorProcess child exited with code null.*',
        '',
        output,
    )

    return output


def assert_no_generator_output(output: str) -> None:
    assert 'prisma:GeneratorProcess' not in _remove_known_warnings(output)


def test_model_name_python_keyword(testdir: Testdir) -> None:
    """Model name shadowing a python keyword is not allowed"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model from {{
            id   String @id
            name String
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert 'Model name "from" shadows a Python keyword; use a different model name with \'@@map("from")\'' in str(
        exc.value.output, 'utf-8'
    )


def test_model_name_lowercase_python_keyword(testdir: Testdir) -> None:
    """Model name that when transformed to lowercase a python keyword is not allowed"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model Class {{
            id   String @id
            name String
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Model name "Class" results in a client property that shadows a Python keyword; use a different model name with \'@@map("Class")\''
        in str(exc.value.output, 'utf-8')
    )


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
        'use a different field name with \'@map("json")\'' in str(exc.value.output, 'utf-8')
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

    assert 'Field name "from" shadows a Python keyword; use a different field name with \'@map("from")\'' in str(
        exc.value.output, 'utf-8'
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
        'Field name "order_by" shadows an internal keyword; ' 'use a different field name with \'@map("order_by")\''
    ) in str(exc.value.output, 'utf-8')


def test_custom_model_instance_name_not_valid_identifier(
    testdir: Testdir,
) -> None:
    schema = (
        testdir.SCHEMA_HEADER
        + """
        /// @Python(instance_name: "1")
        model User {{
            id String @id
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert 'Custom Model instance_name "1" is not a valid Python identifier' in str(exc.value.output, 'utf-8')


def test_native_binary_target_no_warning(testdir: Testdir) -> None:
    """binaryTargets only being native does not raise warning"""
    with temp_env_update({'PRISMA_PY_DEBUG': '0'}):
        result = testdir.generate(options='binaryTargets = ["native"]')

    stdout = _remove_known_warnings(result.stdout.decode('utf-8'))
    assert 'Warning' not in stdout
    assert 'binaryTargets option' not in stdout
    assert_no_generator_output(stdout)


def test_binary_targets_warning(testdir: Testdir) -> None:
    """Binary targets option being present raises a warning"""
    with temp_env_update({'PRISMA_PY_DEBUG': '0'}):
        result = testdir.generate(options='binaryTargets = ["native", "rhel-openssl-1.1.x"]')

    stdout = result.stdout.decode('utf-8')
    assert_no_generator_output(stdout)
    assert 'Warning: The binaryTargets option ' 'is not officially supported by Prisma Client Python' in stdout


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
    assert 'The http option has been removed ' 'in favour of the interface option.' in stdout
    assert 'Please remove the http option from ' 'your Prisma schema and replace it with:' in stdout
    assert f'interface = "{new}"' in stdout


def test_decimal_type_experimental(testdir: Testdir) -> None:
    """The Decimal type requires a config flag to be set"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
        model User {{
          id     String @id @default(cuid())
          points Decimal
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    output = str(exc.value.output, 'utf-8')
    assert 'Support for the Decimal type is experimental' in output
    assert 'set the `enable_experimental_decimal` config flag to true' in output


def test_composite_type_not_supported(testdir: Testdir) -> None:
    """Composite types are not supported yet"""
    schema = (
        testdir.default_generator
        + """
        datasource db {{
            provider = "mongodb"
            url      = env("foo")
        }}

        model User {{
            id       String @id @map("_id")
            // settings UserSettings
        }}

        type UserSettings {{
            points Decimal
        }}
    """
    )
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    output = str(exc.value.output, 'utf-8')
    assert 'Composite types are not supported yet.' in output
    assert 'https://github.com/RobertCraigie/prisma-client-py/issues/314' in output
