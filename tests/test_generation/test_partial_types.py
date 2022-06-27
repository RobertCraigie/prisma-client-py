# pyright: reportUnusedFunction=false

import subprocess

import pytest
from prisma._types import Literal
from ..utils import Testdir


SCHEMA = """
datasource db {{
  provider = "postgres"
  url      = env("DB_URL")
}}

generator db {{
  provider = "coverage run -m prisma"
  output = "{output}"
  {options}
}}

model Post {{
  id          String     @id @default(cuid())
  created_at  DateTime   @default(now())
  updated_at  DateTime   @updatedAt
  title       String
  published   Boolean
  desc        String?
  meta        Json?
  comments    Comment[]
  author_id   String
  author      User      @relation(fields: [author_id], references: [id])
  thumbnail   Bytes?
}}

model Comment {{
  id           String   @id @default(cuid())
  created_at   DateTime @default(now())
  updated_at   DateTime @updatedAt
  content      String
  post         Post?    @relation(fields: [post_id], references: [id])
  post_id      String?
}}

model User {{
  id           String   @id @default(cuid())
  created_at   DateTime @default(now())
  updated_at   DateTime @updatedAt
  name         String
  bytes        Bytes
  bytes_list   Bytes[]
  posts        Post[]
}}

model Foo {{
  id   String @id @default(cuid())
  text String
}}
"""


@pytest.mark.parametrize(
    'location,options',
    [
        ('prisma/partial_types.py', ''),
        (
            'prisma/partial_types.py',
            'partial_type_generator = "prisma/partial_types.py"',
        ),
        (
            'scripts/partials_generator.py',
            'partial_type_generator = "scripts.partials_generator"',
        ),
    ],
)
def test_partial_types(testdir: Testdir, location: str, options: str) -> None:
    """Grouped tests for partial types to improve test speed"""

    def tests() -> None:  # mark: filedef
        import sys
        import datetime
        from typing import Type, Dict, Iterator, Any, Tuple, Set, Optional
        from pydantic import BaseModel
        from prisma import Base64
        from prisma.partials import (  # type: ignore[attr-defined]
            # pyright: reportGeneralTypeIssues = false
            PostWithoutDesc,
            PostOptionalPublished,
            PostRequiredDesc,
            PostOnlyId,
            PostNoRelations,
            PostOptionalInclude,
            PostRequiredAuthor,
            PostModifiedAuthor,
            UserModifiedPosts,
            UserBytesList,
        )

        base_fields = {
            'id': True,
            'created_at': True,
            'updated_at': True,
            'title': True,
            'published': True,
            'desc': False,
            'meta': False,
            'comments': False,
            'author': False,
            'author_id': True,
            'thumbnail': False,
        }

        def common_entries(
            dct: Dict[str, Any], other: Dict[str, Any]
        ) -> Iterator[Tuple[str, Any, Any]]:
            for key in dct.keys() & other.keys():
                yield key, dct[key], other[key]

        def assert_expected(
            model: Type[BaseModel],
            fields: Dict[str, bool],
            removed: Optional[Set[str]],
        ) -> None:
            for field, required, info in common_entries(
                fields, model.__fields__
            ):
                assert info.name == field
                assert info.required == required

            if removed is None:
                removed = set()

            assert fields.keys() - model.__fields__.keys() == removed

        def test_without_desc() -> None:
            """Removing one field"""
            assert_expected(PostWithoutDesc, base_fields, {'desc'})

        def test_optional_published() -> None:
            """Making one field optional"""
            assert_expected(
                PostOptionalPublished,
                fields={**base_fields, 'published': False},
                removed=None,
            )

        def test_required_desc() -> None:
            """Making one field required"""
            assert_expected(
                PostRequiredDesc,
                fields={**base_fields, 'desc': True},
                removed=None,
            )

        def test_required_relational_author() -> None:
            """Making relational field required"""
            assert_expected(
                PostRequiredAuthor,
                fields={**base_fields, 'author': True},
                removed=None,
            )

        def test_only_id() -> None:
            """Removing all fields except from one"""
            assert_expected(
                PostOnlyId,
                fields=base_fields,
                removed={
                    'created_at',
                    'updated_at',
                    'title',
                    'published',
                    'desc',
                    'meta',
                    'comments',
                    'author',
                    'author_id',
                    'thumbnail',
                },
            )

        def test_optional_include() -> None:
            """Both including and making optional on the same field"""
            assert_expected(
                PostOptionalInclude,
                fields={**base_fields, 'title': False},
                removed={
                    'id',
                    'created_at',
                    'updated_at',
                    'published',
                    'desc',
                    'meta',
                    'comments',
                    'author',
                    'author_id',
                    'thumbnail',
                },
            )

        def test_modified_relational_type() -> None:
            """Changing one-to-one relational field type"""
            assert_expected(PostModifiedAuthor, base_fields, None)

            field = PostModifiedAuthor.__fields__['author']
            assert field.type_.__name__ == 'UserOnlyName'
            assert field.type_.__module__ == 'prisma.partials'

        def test_exclude_relations() -> None:
            """Removing all relational fields using `exclude_relations`"""
            assert_expected(
                PostNoRelations,
                base_fields,
                removed={
                    'author',
                    'comments',
                },
            )

        def test_modified_relational_list_type() -> None:
            """Changing one-to-many relation field type"""
            UserModifiedPosts(
                id='1',
                name='Robert',
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                posts=[PostOnlyId(id='2')],
            )
            field = UserModifiedPosts.__fields__['posts']
            assert field.type_.__name__ == 'PostOnlyId'
            assert field.type_.__module__ == 'prisma.partials'

            if sys.version_info >= (3, 7):
                assert field.outer_type_._name == 'List'
            else:
                assert field.outer_type_.__name__ == 'List'

            assert field.outer_type_.__module__ == 'typing'

        def test_bytes() -> None:
            """Ensure Base64 fields can be used"""
            # mock prisma behaviour
            model = UserBytesList.parse_obj(
                {
                    'bytes': str(Base64.encode(b'bar')),
                    'bytes_list': [
                        str(Base64.encode(b'foo')),
                        str(Base64.encode(b'baz')),
                    ],
                }
            )
            assert model.bytes == Base64.encode(b'bar')
            assert model.bytes_list == [
                Base64.encode(b'foo'),
                Base64.encode(b'baz'),
            ]

    def generator() -> None:  # mark: filedef
        from prisma.models import Post, User

        User.create_partial('UserOnlyName', include={'name'})

        Post.create_partial('PostWithoutDesc', exclude=['desc'])
        Post.create_partial('PostOptionalPublished', optional=['published'])
        Post.create_partial('PostRequiredDesc', required=['desc'])
        Post.create_partial('PostOnlyId', include={'id'})
        Post.create_partial(
            'PostOptionalInclude', include={'title'}, optional={'title'}
        )
        Post.create_partial('PostRequiredAuthor', required=['author'])
        Post.create_partial(
            'PostModifiedAuthor', relations={'author': 'UserOnlyName'}
        )
        Post.create_partial('PostNoRelations', exclude_relational_fields=True)

        User.create_partial(
            'UserModifiedPosts',
            exclude={'bytes', 'bytes_list'},  # type: ignore
            relations={'posts': 'PostOnlyId'},
        )
        User.create_partial('UserBytesList', include={'bytes', 'bytes_list'})  # type: ignore

    testdir.make_from_function(generator, name=location)
    testdir.generate(SCHEMA, options)
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=10)


@pytest.mark.parametrize(
    'argument', ['exclude', 'include', 'required', 'optional']
)
def test_partial_types_incorrect_key(
    testdir: Testdir,
    argument: Literal['exclude', 'include', 'required', 'optional'],
) -> None:
    """Invalid field name raises error"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial('PostWithoutFoo', **{argument: ['foo']})  # type: ignore

    testdir.make_from_function(
        generator, name='prisma/partial_types.py', argument=argument
    )

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    assert 'foo is not a valid Post / PostWithoutFoo field' in str(
        exc.value.output
    )


def test_partial_types_same_required_and_optional(testdir: Testdir) -> None:
    """Making the same field required and optional raises an error"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial(
            'PostPartial',
            required={'desc', 'published', 'title'},
            optional={
                'desc',
                'published',
            },
        )

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    assert 'Cannot make the same field(s) required and optional' in str(
        exc.value.output
    )


def test_partial_types_excluded_required(testdir: Testdir) -> None:
    """Excluding and requiring the same field raises an error"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial(
            'PostPartial',
            exclude={'desc'},
            required={
                'desc',
            },
        )

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    assert 'desc is not a valid Post / PostPartial field' in str(
        exc.value.output
    )


def test_partial_type_generator_not_found(testdir: Testdir) -> None:
    """Unknown partial type generator option value raises an error"""
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA, 'partial_type_generator = "foo.bar.baz"')

    output = str(exc.value.output)
    assert 'ValidationError' in output
    assert 'generator -> config -> partial_type_generator' in output
    assert 'Could not find a python file or module at foo.bar.baz' in output


def test_partial_type_generator_error_while_running(testdir: Testdir) -> None:
    """Exception ocurring while running partial type generator logs exception"""

    def generator() -> None:  # mark: filedef
        import foo  # type: ignore[import]

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    output = str(exc.value.output)
    assert 'prisma/partial_types.py' in output
    assert "No module named \\'foo\\'" in output
    assert (
        'An exception ocurred while running the partial type generator'
        in output
    )


def test_partial_type_already_created(testdir: Testdir) -> None:
    """Creating same partial type twice raises error"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        for _ in range(2):
            Post.create_partial(
                'PostPartial',
                exclude={'desc'},
            )

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    output = str(exc.value.output)
    assert 'prisma/partial_types.py' in output
    assert 'Partial type "PostPartial" has already been created.' in output
    assert (
        'An exception ocurred while running the partial type generator'
        in output
    )


def test_unknown_partial_type(testdir: Testdir) -> None:
    """Modifying relational field type to unknown partial type raises error"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial('PostPartial', relations={'author': 'UnknownUser'})

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    output = str(exc.value.output)
    assert 'ValueError' in output
    assert 'prisma/partial_types.py' in output
    assert 'Unknown partial type: "UnknownUser"' in output
    assert (
        'An exception ocurred while running the partial type generator'
        in output
    )
    assert (
        'Did you remember to generate the UnknownUser type before this one?'
        in output
    )


def test_passing_type_for_excluded_field(testdir: Testdir) -> None:
    """Passing relational type for an excluded field raises error"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Post, User

        User.create_partial('CustomUser')
        Post.create_partial(
            'PostPartial',
            exclude={'author'},
            relations={'author': 'CustomUser'},
        )

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    output = str(exc.value.output)
    assert 'ValueError' in output
    assert 'prisma/partial_types.py' in output
    assert 'author is not a valid Post / PostPartial field' in output
    assert (
        'An exception ocurred while running the partial type generator'
        in output
    )


def test_partial_type_types_non_relational(testdir: Testdir) -> None:
    """Passing non-relational field to relations raises an error"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial('Placeholder')
        Post.create_partial(
            'PostPartial',
            relations={'published': 'Placeholder'},  # type: ignore[dict-item]
        )

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    output = str(exc.value.output)
    assert 'prisma/partial_types.py' in output
    assert 'prisma.errors.UnknownRelationalFieldError' in output
    assert (
        'An exception ocurred while running the partial type generator'
        in output
    )
    assert (
        'Field: "published" either does not exist or is not a relational field on the Post model'
        in output
    )


def test_partial_type_relations_no_relational_fields(testdir: Testdir) -> None:
    """Passing relations option to model with no relational fields raises an error"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Foo  # type: ignore[attr-defined]

        Foo.create_partial('Placeholder', relations={'wow': 'Placeholder'})

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    output = exc.value.output.decode('utf-8')
    assert 'prisma/partial_types.py' in output
    assert 'ValueError' in output
    assert (
        'An exception ocurred while running the partial type generator'
        in output
    )
    assert 'Model: "Foo" has no relational fields.' in output


def test_exclude_relational_fields_and_relations_exclusive(
    testdir: Testdir,
) -> None:
    """exclude_relational_fields and relations cannot be passed at the same time"""

    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial(
            'Placeholder',
            relations={'author': 'Placeholder'},
            exclude_relational_fields=True,
        )

    testdir.make_from_function(generator, name='prisma/partial_types.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    output = exc.value.output.decode('utf-8')
    assert 'prisma/partial_types.py' in output
    assert 'ValueError' in output
    assert (
        'An exception ocurred while running the partial type generator'
        in output
    )
    assert (
        'exclude_relational_fields and relations are mutually exclusive'
        in output
    )
