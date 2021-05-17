import subprocess
from typing import Optional

import pytest
from prisma._types import Literal
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

model Post {{
  id          String     @id @default(cuid())
  createdAt   DateTime   @default(now())
  updated_at  DateTime   @updatedAt
  Title       String
  Published   Boolean
  desc        String?
  comments    Comment[]
  author_id   String
  author      User      @relation(fields: [author_id], references: [id])
}}

model Comment {{
  id           String   @id @default(cuid())
  created_at   DateTime @default(now())
  updated_at   DateTime @updatedAt
  content      String
  Post         Post?    @relation(fields: [post_id], references: [id])
  post_id      String?
}}

model User {{
  id           String   @id @default(cuid())
  created_at   DateTime @default(now())
  updated_at   DateTime @updatedAt
  name         String
  posts        Post[]
}}
'''


@pytest.mark.parametrize(
    'location,options',
    [
        ('.prisma/partials.py', ''),
        ('.prisma/partials.py', 'partial_type_generator = ".prisma/partials.py"'),
        (
            'scripts/partials_generator.py',
            'partial_type_generator = "scripts.partials_generator"',
        ),
    ],
)
def test_partial_types(testdir: Testdir, location: str, options: str) -> None:
    def tests() -> None:  # pylint: disable=all  mark: filedef
        from typing import Type, Dict, Iterator, Any, Tuple, Set, Optional
        from pydantic import BaseModel
        from prisma.partials import (  # type: ignore[attr-defined]
            PostWithoutDesc,
            PostOptionalPublished,
            PostRequiredDesc,
            PostOnlyId,
            PostOptionalInclude,
            PostRequiredAuthor,
        )

        base_fields = {
            'id': True,
            'created_at': True,
            'updated_at': True,
            'title': True,
            'published': True,
            'desc': False,
            'comments': False,
            'author': False,
            'author_id': True,
        }

        def common_entries(
            dct: Dict[str, Any], other: Dict[str, Any]
        ) -> Iterator[Tuple[str, Any, Any]]:
            for key in dct.keys() & other.keys():
                yield key, dct[key], other[key]

        def assert_expected(
            model: Type[BaseModel], fields: Dict[str, bool], removed: Optional[Set[str]]
        ) -> None:
            for field, required, info in common_entries(fields, model.__fields__):
                assert info.name == field
                assert info.required == required

            if removed is None:
                removed = set()

            assert fields.keys() - model.__fields__.keys() == removed

        def test_without_desc() -> None:
            assert_expected(PostWithoutDesc, base_fields, {'desc'})

        def test_optional_published() -> None:
            assert_expected(
                PostOptionalPublished,
                fields={**base_fields, 'published': False},
                removed=None,
            )

        def test_required_desc() -> None:
            assert_expected(
                PostRequiredDesc, fields={**base_fields, 'desc': True}, removed=None
            )

        def test_required_relational_author() -> None:
            assert_expected(
                PostRequiredAuthor, fields={**base_fields, 'author': True}, removed=None
            )

        def test_only_id() -> None:
            assert_expected(
                PostOnlyId,
                fields=base_fields,
                removed={
                    'created_at',
                    'updated_at',
                    'title',
                    'published',
                    'desc',
                    'comments',
                    'author',
                    'author_id',
                },
            )

        def test_optional_include() -> None:
            assert_expected(
                PostOptionalInclude,
                fields={**base_fields, 'title': False},
                removed={
                    'id',
                    'created_at',
                    'updated_at',
                    'published',
                    'desc',
                    'comments',
                    'author',
                    'author_id',
                },
            )

    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial('PostWithoutDesc', exclude=['desc'])
        Post.create_partial('PostOptionalPublished', optional=['published'])
        Post.create_partial('PostRequiredDesc', required=['desc'])
        Post.create_partial('PostOnlyId', include={'id'})
        Post.create_partial(
            'PostOptionalInclude', include={'title'}, optional={'title'}
        )
        Post.create_partial('PostRequiredAuthor', required=['author'])

    testdir.make_from_function(generator, name=location)
    testdir.generate(SCHEMA, options)
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=6)


@pytest.mark.parametrize('argument', ['exclude', 'include', 'required', 'optional'])
def test_partial_types_incorrect_key(
    testdir: Testdir, argument: Literal['exclude', 'include', 'required', 'optional']
) -> None:
    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial('PostWithoutFoo', **{argument: ['foo']})  # type: ignore

    testdir.make_from_function(generator, name='.prisma/partials.py', argument=argument)

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    assert 'foo is not a valid Post field' in str(exc.value.output)


def test_partial_types_same_required_and_optional(testdir: Testdir) -> None:
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

    testdir.make_from_function(generator, name='.prisma/partials.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    assert "Cannot make the same field(s) required and optional" in str(
        exc.value.output
    )


def test_partial_types_excluded_required(testdir: Testdir) -> None:
    def generator() -> None:  # mark: filedef
        from prisma.models import Post

        Post.create_partial(
            'PostPartial',
            exclude={'desc'},
            required={
                'desc',
            },
        )

    testdir.make_from_function(generator, name='.prisma/partials.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    assert 'desc is not a valid Post field' in str(exc.value.output)


def test_partial_type_generator_not_found(testdir: Testdir) -> None:
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA, 'partial_type_generator = "foo.bar.baz"')

    output = str(exc.value.output)
    assert 'ValidationError' in output
    assert 'generator -> config -> partial_type_generator' in output
    assert 'Could not find a python file or module at foo.bar.baz' in output


def test_partial_type_generator_error_while_running(testdir: Testdir) -> None:
    def generator() -> None:  # mark: filedef
        import foo  # type: ignore[import]

    testdir.make_from_function(generator, name='.prisma/partials.py')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(SCHEMA)

    output = str(exc.value.output)
    assert '.prisma/partials.py' in output
    assert 'No module named \\\'foo\\\'' in output
    assert 'An exception ocurred while running the partial type generator' in output
