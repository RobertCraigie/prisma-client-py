import os
import sys
import datetime
import subprocess

import pytest


SCHEMA = '''
datasource db {{
    provider = "sqlite"
    url      = "file:dev.db"
}}

generator db {{
    provider = "python3 -m prisma"
    output = "{output}"
    {options}
}}

model Post {{
    id          String   @default(cuid()) @id
    createdAt   DateTime @default(now())
    updated_at  DateTime @updatedAt
    Title       String
    Published Boolean
    desc        String?
}}
'''


@pytest.fixture
def tmpdir(tmpdir):
    generate = tmpdir.generate
    tmpdir.generate = lambda *a: generate(SCHEMA, *a)
    return tmpdir


def test_transform_fields_none(tmpdir):
    tmpdir.generate('transform_fields = "none"')

    from models import Post

    post = Post(
        id='1',
        createdAt=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        Title='title',
        Published=False,
    )
    assert post.id == '1'
    assert isinstance(post.createdAt, datetime.datetime)
    assert isinstance(post.updated_at, datetime.datetime)
    assert post.Title == 'title'
    assert post.Published is False

    with pytest.raises(AttributeError):
        post.title


@pytest.mark.parametrize('explicit', [True, False])
def test_transform_fields_snake_case(tmpdir, explicit):
    if explicit:
        tmpdir.generate('transform_fields = "snake_case"')
    else:
        tmpdir.generate('')

    from models import Post

    post = Post(
        id='1',
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        title='title',
        published=False,
    )
    assert post.id == '1'
    assert isinstance(post.created_at, datetime.datetime)
    assert isinstance(post.updated_at, datetime.datetime)
    assert post.title == 'title'
    assert post.published is False

    with pytest.raises(AttributeError):
        post.Title


def test_transform_fields_camel_case(tmpdir):
    tmpdir.generate('transform_fields = "camelCase"')

    from models import Post

    post = Post(
        id='1',
        createdAt=datetime.datetime.utcnow(),
        updatedAt=datetime.datetime.utcnow(),
        title='title',
        published=False,
    )
    assert post.id == '1'
    assert isinstance(post.createdAt, datetime.datetime)
    assert isinstance(post.updatedAt, datetime.datetime)
    assert post.title == 'title'
    assert post.published is False

    with pytest.raises(AttributeError):
        post.Published


def test_transform_fields_pascal_case(tmpdir):
    tmpdir.generate('transform_fields = "PascalCase"')

    from models import Post

    post = Post(
        Id='1',
        CreatedAt=datetime.datetime.utcnow(),
        UpdatedAt=datetime.datetime.utcnow(),
        Title='title',
        Published=False,
    )
    assert post.Id == '1'
    assert isinstance(post.CreatedAt, datetime.datetime)
    assert isinstance(post.UpdatedAt, datetime.datetime)
    assert post.Title == 'title'
    assert post.Published is False

    with pytest.raises(AttributeError):
        post.created_at
