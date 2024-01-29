from __future__ import annotations

import datetime
from typing import Any, Optional

import pytest
from pydantic import BaseModel
from inline_snapshot import snapshot

from prisma import PrismaMethod, models
from prisma.bases import _PrismaModel as PrismaModel
from prisma.utils import _NoneType
from prisma.errors import UnknownModelError, UnknownRelationalFieldError
from prisma._compat import PYDANTIC_V2
from prisma._builder import QueryBuilder, serializer
from prisma.metadata import PRISMA_MODELS, RELATIONAL_FIELD_MAPPINGS

# TODO: more tests
# TODO: cleanup registered serializers
# TODO: these tests should be schema agnostic
#       one schema should be used for all these tests
#       and only changed when needed for these tests
#       otherwise, simply adding a field to a model
#       will break these tests


def build_query(
    method: PrismaMethod,
    arguments: dict[str, Any],
    **kwargs: Any,
) -> str:
    return QueryBuilder(
        method=method,
        arguments=arguments,
        **kwargs,
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()


def test_basic_building() -> None:
    """Standard builder usage with and without a model"""
    query = QueryBuilder(
        method='find_unique',
        model=models.User,
        arguments={'where': {'id': '1'}},
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findUniqueUser
  (
    where: {
      id: "1"
    }
  )
  {
    id
    name
    email
    created_at
  }
}\
"""
    )

    query = QueryBuilder(
        method='query_raw',
        arguments={'where': {'id': '1'}},
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
mutation {
  result: queryRaw
  (
    where: {
      id: "1"
    }
  )
}\
"""
    )


def test_invalid_include() -> None:
    """Invalid include field raises error"""
    with pytest.raises(UnknownRelationalFieldError) as exception:
        QueryBuilder(
            method='find_unique',
            model=models.User,
            arguments={
                'include': {
                    'hello': True,
                }
            },
            prisma_models=PRISMA_MODELS,
            relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
        ).build_query()

    assert exception.match('Field: "hello" either does not exist or is not a relational field on the User model')


def test_include_no_model() -> None:
    """Trying to include a field without acess to a model raises an error"""
    with pytest.raises(ValueError) as exc:
        build_query(
            method='query_raw',
            arguments={'include': {'posts': True}},
        )

    assert exc.match('Cannot include fields when model is None.')


def test_include_with_arguments() -> None:
    """Including a field with filters"""
    query = QueryBuilder(
        method='find_unique',
        model=models.User,
        arguments={'where': {'id': 1}, 'include': {'posts': {'where': {'id': 1}}}},
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findUniqueUser
  (
    where: {
      id: 1
    }
  )
  {
    id
    name
    email
    created_at
    posts(
      where: {
        id: 1
      }
    )
    {
      id
      created_at
      updated_at
      title
      published
      views
      desc
      author_id
    }
  }
}\
"""
    )


def test_raw_queries() -> None:
    """Raw queries serialise paramaters to JSON"""
    query = QueryBuilder(
        method='query_raw',
        arguments={
            'query': 'SELECT * FROM User where id = $1',
            'parameters': ['1263526'],
        },
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
mutation {
  result: queryRaw
  (
    query: "SELECT * FROM User where id = $1"
    parameters: "[\\"1263526\\"]"
  )
}\
"""
    )


def test_datetime_serialization_tz_aware() -> None:
    """Serializing a timezone aware datetime converts to UTC"""
    query = QueryBuilder(
        method='find_unique',
        model=models.Post,
        arguments={'where': {'created_at': datetime.datetime(1985, 10, 26, 1, 1, 1, tzinfo=datetime.timezone.max)}},
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findUniquePost
  (
    where: {
      created_at: "1985-10-25T01:02:01+00:00"
    }
  )
  {
    id
    created_at
    updated_at
    title
    published
    views
    desc
    author_id
  }
}\
"""
    )


def test_datetime_serialization_tz_unaware() -> None:
    """Serializing a timezone naive datetime converts to UTC"""
    query = QueryBuilder(
        method='find_unique',
        model=models.Post,
        arguments={
            'where': {
                'created_at': datetime.datetime(1985, 10, 26, 1, 1, 1),
            }
        },
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findUniquePost
  (
    where: {
      created_at: "1985-10-26T01:01:01+00:00"
    }
  )
  {
    id
    created_at
    updated_at
    title
    published
    views
    desc
    author_id
  }
}\
"""
    )


def test_unicode() -> None:
    """Serializing unicode strings does not convert to ASCII"""
    query = QueryBuilder(
        method='find_unique',
        model=models.User,
        arguments={
            'where': {
                'name': '❤',
            }
        },
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findUniqueUser
  (
    where: {
      name: "❤"
    }
  )
  {
    id
    name
    email
    created_at
  }
}\
"""
    )


def test_unknown_model() -> None:
    """Passing unknown model raises an error"""

    class FooModel(PrismaModel):
        __prisma_model__ = 'Foo'

    with pytest.raises(UnknownModelError) as exc:
        QueryBuilder(
            method='find_unique',
            model=FooModel,
            arguments={},
            prisma_models=PRISMA_MODELS,
            relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
        ).build_query()

    assert exc.match(r'Model: "Foo" does not exist\.')


def test_unserializable_type() -> None:
    """Passing an unserializable type raises an error"""
    with pytest.raises(TypeError) as exc:
        QueryBuilder(
            method='find_first',
            arguments={'where': QueryBuilder},
            prisma_models=PRISMA_MODELS,
            relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
        ).build_query()

    assert exc.match(r'Type <class \'prisma._builder.QueryBuilder\'> not serializable')


def test_unserializable_instance() -> None:
    """Passing an unserializable instance raises an error"""
    with pytest.raises(TypeError) as exc:
        QueryBuilder(
            method='find_first',
            arguments={
                'where': _NoneType(),
            },
            prisma_models=PRISMA_MODELS,
            relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
        ).build_query()

    assert exc.match(r'Type <class \'prisma.utils._NoneType\'> not serializable')


def test_custom_serialization() -> None:
    """Registering a custom serializer serializes as expected"""

    class Foo:
        def __init__(self, arg: int) -> None:
            self.arg = arg

    @serializer.register(Foo)
    def custom_serializer(inst: Foo) -> int:  # pyright: ignore[reportUnusedFunction]
        return inst.arg

    query = QueryBuilder(
        method='find_unique',
        model=models.Post,
        arguments={
            'where': {
                'title': Foo(1),
            }
        },
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findUniquePost
  (
    where: {
      title: 1
    }
  )
  {
    id
    created_at
    updated_at
    title
    published
    views
    desc
    author_id
  }
}\
"""
    )


def test_select() -> None:
    """Selecting a subset of fields"""

    class OtherModel(PrismaModel):
        name: str
        __prisma_model__ = 'User'

    class CustomModel(PrismaModel):
        published: bool
        author: Optional[OtherModel]

        __prisma_model__ = 'Post'

    if not PYDANTIC_V2:
        CustomModel.update_forward_refs(**locals())  # pyright: ignore[reportDeprecated]

    query = QueryBuilder(
        method='find_first',
        model=CustomModel,
        arguments={
            'where': {
                'title': 'Foo',
            },
        },
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findFirstPost
  (
    where: {
      title: "Foo"
    }
  )
  {
    published
  }
}\
"""
    )

    with pytest.raises(UnknownRelationalFieldError) as exc:
        QueryBuilder(
            method='find_unique',
            model=OtherModel,
            arguments={
                'include': {
                    'posts': True,
                },
            },
            prisma_models=PRISMA_MODELS,
            relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
        ).build_query()

    assert exc.match(r'Field: "posts" either does not exist or is not a relational field on the OtherModel model')

    query = QueryBuilder(
        method='find_first',
        model=CustomModel,
        arguments={
            'include': {
                'author': True,
            },
        },
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findFirstPost
  {
    published
    author {
      name
    }
  }
}\
"""
    )


def test_select_non_prisma_model_basemodel() -> None:
    """Fields that point to a `BaseModel` but do not set the `__prisma_model__`
    class variable are included by default as scalar fields.
    """

    class OtherModel(PrismaModel):
        name: str
        __prisma_model__ = 'User'

    class TypedJson(BaseModel):
        foo: str

    class CustomModel(PrismaModel):
        published: bool
        my_json_blob: TypedJson
        author: Optional[OtherModel]

        __prisma_model__ = 'Post'

    if not PYDANTIC_V2:
        CustomModel.update_forward_refs(**locals())  # pyright: ignore[reportDeprecated]

    query = QueryBuilder(
        method='find_first',
        model=CustomModel,
        arguments={
            'where': {
                'title': 'Foo',
            },
        },
        prisma_models=PRISMA_MODELS,
        relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
    ).build_query()
    assert query == snapshot(
        """\
query {
  result: findFirstPost
  (
    where: {
      title: "Foo"
    }
  )
  {
    published
    my_json_blob
  }
}\
"""
    )


@pytest.mark.skipif(PYDANTIC_V2, reason='Pydantic v2 has better forward refs support')
def test_forward_reference_error() -> None:
    """If a Model has forward references and doesn't call `update_forward_refs()` then we can't
    tell if a given field should be included by default. Hence the sanity check here.
    """

    class TypedJson(BaseModel):
        foo: str

    class CustomModel(PrismaModel):
        meta: TypedJson

        __prisma_model__ = 'Post'

    with pytest.raises(
        RuntimeError, match=r'Forward references must be evaluated using CustomModel\.update_forward_refs\(\)'
    ):
        QueryBuilder(
            method='find_first',
            model=CustomModel,
            arguments={},
            prisma_models=PRISMA_MODELS,
            relational_field_mappings=RELATIONAL_FIELD_MAPPINGS,
        ).build_query()
