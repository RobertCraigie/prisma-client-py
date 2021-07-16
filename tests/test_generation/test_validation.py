import subprocess

import pytest

from ..utils import Testdir


def test_field_name_basemodel_attribute(testdir: Testdir) -> None:
    schema = '''
        datasource db {{
          provider = "sqlite"
          url      = "file:dev.db"
        }}

        generator db {{
          provider = "coverage run -m prisma"
          output = "{output}"
          {options}
        }}

        model User {{
            id   String @id
            json String
        }}
    '''
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(schema=schema)

    assert (
        'Field name "json" shadows a BaseModel attribute; use a different field name with \'@map("json")\''
        in str(exc.value.output, 'utf-8')
    )


def test_field_name_python_keyword(testdir: Testdir) -> None:
    schema = '''
        datasource db {{
          provider = "sqlite"
          url      = "file:dev.db"
        }}

        generator db {{
          provider = "coverage run -m prisma"
          output = "{output}"
          {options}
        }}

        model User {{
            id   String @id
            from String
        }}
    '''
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
