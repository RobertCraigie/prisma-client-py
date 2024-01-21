import subprocess

import pytest

from prisma.utils import temp_env_update

from ..utils import Testdir


def test_one_datasource_allowed(testdir: Testdir) -> None:
    """Prisma only allows one datasource"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
        datasource db2 {{
          provider = "sqlite"
          url      = "file:dev-2.db"
        }}
    """
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
    """Prisma generator output can be resolved from an env variable"""
    schema = """
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
    """

    with temp_env_update({'PRISMA_TEST_ASSUMPTIONS_OUTPUT': str(testdir.path / 'prisma')}):
        testdir.generate(schema=schema)


def test_relational_field_cannot_be_unique(testdir: Testdir) -> None:
    """Prisma does not allow relational fields to be unique"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
    model User {{
        id    Int    @id @default(autoincrement())
        name  String
        posts Post[]
    }}

    model Post {{
        id         Int    @id @default(autoincrement())
        author     User   @relation(fields: [author_id], references: [id]) @unique
        author_id  Int
    }}
    """
    )

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    output = exc.value.output.decode('utf-8')
    assert 'The field `author` is a relation field and cannot be marked with `unique`.' in output


def test_enum_same_name_as_model_disallowed(testdir: Testdir) -> None:
    """Ensure an Enum cannot be defined with the same name as a model"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
    model User {{
        id    Int    @id @default(autoincrement())
        name  String
    }}

    enum User {{
        FOO
        BAR
    }}
    """
    )

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    output = exc.value.output.decode('utf-8')
    assert 'The enum "User" cannot be defined because a model with that name already exists.' in output


def test_multiple_compund_ids_disallowed(testdir: Testdir) -> None:
    """Multiple @@id() annotations are not allowed on the same model"""
    schema = (
        testdir.SCHEMA_HEADER
        + """
    model User {{
        name    String
        surname String
        points  Int
        email   String

        @@id([name, surname])
        @@id([points, email])
    }}
    """
    )

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    output = exc.value.output.decode('utf-8')
    assert 'Attribute "@id" can only be defined once.' in output


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
        'The field `name_surname` clashes with the `@@unique` name. '
        'Please resolve the conflict by providing a custom id name: `@@unique([...], name: "custom_name")`'
    ) in str(exc.value.output, 'utf-8')


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
        "The field `name_surname` clashes with the `@@id` attribute's name. "
        'Please resolve the conflict by providing a custom id name: `@@id([...], name: "custom_name")`'
    ) in str(exc.value.output, 'utf-8')
