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

    with temp_env_update(
        {'PRISMA_TEST_ASSUMPTIONS_OUTPUT': str(testdir.path / 'prisma')}
    ):
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
    assert (
        'The field `author` is a relation field and cannot be marked with `unique`.'
        in output
    )


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
    assert (
        'The enum "User" cannot be defined because a model with that name already exists.'
        in output
    )


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
    assert 'Attribute "@id" is defined twice.' in output
