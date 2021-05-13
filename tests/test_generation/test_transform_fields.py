import datetime
import pytest
from ..utils import Testdir


SCHEMA = '''
datasource db {{
    provider = "sqlite"
    url      = "file:dev.db"
}}

generator db {{
    provider = "coverage run -m prisma"
    output = "{output}"
    {options}
}}

model Entry {{
    id          String   @default(cuid()) @id
    createdAt   DateTime @default(now())
    updated_at  DateTime @updatedAt
    Title       String
    Published Boolean
    desc        String?
}}
'''


def test_transform_fields_none(testdir: Testdir) -> None:
    def tests() -> None:  # pylint: disable=all mark: filedef
        import datetime
        import pytest
        from prisma.models import Entry  # type: ignore[attr-defined]

        def test_transform_fields_none() -> None:
            entry = Entry(
                id='1',
                createdAt=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                Title='title',
                Published=False,
            )
            assert entry.id == '1'
            assert isinstance(entry.createdAt, datetime.datetime)
            assert isinstance(entry.updated_at, datetime.datetime)
            assert entry.Title == 'title'
            assert entry.Published is False

            with pytest.raises(AttributeError):
                assert entry.title

    testdir.generate(SCHEMA, 'transform_fields = "none"')
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=1)


@pytest.mark.parametrize('explicit', [True, False])
def test_transform_fields_snake_case(testdir: Testdir, explicit: bool) -> None:
    def tests() -> None:  # pylint: disable=all mark: filedef
        import datetime
        import pytest
        from prisma.models import Entry  # type: ignore[attr-defined]

        def test_transform_fields_snake_case() -> None:
            entry = Entry(
                id='1',
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                title='title',
                published=False,
            )
            assert entry.id == '1'
            assert isinstance(entry.created_at, datetime.datetime)
            assert isinstance(entry.updated_at, datetime.datetime)
            assert entry.title == 'title'
            assert entry.published is False

            with pytest.raises(AttributeError):
                assert entry.Title  # pylint: disable=no-member

    if explicit:
        testdir.generate(SCHEMA, 'transform_fields = "snake_case"')
    else:
        testdir.generate(SCHEMA)

    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=1)


def test_transform_fields_camel_case(testdir: Testdir) -> None:
    def tests() -> None:  # pylint: disable=all mark: filedef
        import datetime
        import pytest
        from prisma.models import Entry  # type: ignore[attr-defined]

        def test_transform_fields_camel_case() -> None:
            entry = Entry(
                id='1',
                createdAt=datetime.datetime.utcnow(),
                updatedAt=datetime.datetime.utcnow(),
                title='title',
                published=False,
            )
            assert entry.id == '1'
            assert isinstance(entry.createdAt, datetime.datetime)
            assert isinstance(entry.updatedAt, datetime.datetime)
            assert entry.title == 'title'
            assert entry.published is False

            with pytest.raises(AttributeError):
                assert entry.Published

    testdir.generate(SCHEMA, 'transform_fields = "camelCase"')
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=1)


def test_transform_fields_pascal_case(testdir: Testdir) -> None:
    def tests() -> None:  # pylint: disable=all mark: filedef
        import datetime
        import pytest
        from prisma.models import Entry  # type: ignore[attr-defined]

        def test_transform_fields_pascal_case() -> None:
            entry = Entry(
                Id='1',
                CreatedAt=datetime.datetime.utcnow(),
                UpdatedAt=datetime.datetime.utcnow(),
                Title='title',
                Published=False,
            )
            assert entry.Id == '1'
            assert isinstance(entry.CreatedAt, datetime.datetime)
            assert isinstance(entry.UpdatedAt, datetime.datetime)
            assert entry.Title == 'title'
            assert entry.Published is False

            with pytest.raises(AttributeError):
                assert entry.created_at

    testdir.generate(SCHEMA, 'transform_fields = "PascalCase"')
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=1)
