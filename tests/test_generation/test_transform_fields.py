import datetime

import pytest

from .utils import Tmpdir


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


def test_transform_fields_none(tmpdir: Tmpdir) -> None:
    # pylint: disable=import-outside-toplevel, no-member
    tmpdir.generate(SCHEMA, 'transform_fields = "none"')

    from models import Post  # type: ignore[import]

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
        assert post.title


@pytest.mark.parametrize('explicit', [True, False])
def test_transform_fields_snake_case(tmpdir: Tmpdir, explicit: bool) -> None:
    # pylint: disable=import-outside-toplevel
    if explicit:
        tmpdir.generate(SCHEMA, 'transform_fields = "snake_case"')
    else:
        tmpdir.generate(SCHEMA, '')

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
        assert post.Title  # pylint: disable=no-member


def test_transform_fields_camel_case(tmpdir: Tmpdir) -> None:
    # pylint: disable=import-outside-toplevel, no-member
    tmpdir.generate(SCHEMA, 'transform_fields = "camelCase"')

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
        assert post.Published


def test_transform_fields_pascal_case(tmpdir: Tmpdir) -> None:
    # pylint: disable=import-outside-toplevel, no-member
    tmpdir.generate(SCHEMA, 'transform_fields = "PascalCase"')

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
        assert post.created_at
