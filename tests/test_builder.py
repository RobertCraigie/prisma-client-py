# fmt: off
# I prefer this way of formatting
import datetime
from typing import Dict, Any

import pytest
from syrupy import SnapshotAssertion
from prisma.utils import _NoneType
from prisma.builder import QueryBuilder, serializer
from prisma.errors import UnknownRelationalFieldError, UnknownModelError

from .utils import assert_query_equals


# TODO: more tests
# TODO: cleanup registered serializers
# TODO: these tests should be schema agnostic
#       one schema should be used for all these tests
#       and only changed when needed for these tests
#       otherwise, simply adding a field to a model
#       will break these tests


def build_query(
    method: str,
    operation: str,
    arguments: Dict[str, Any],
    **kwargs: Any,
) -> str:
    return QueryBuilder(
        method=method,
        operation=operation,
        arguments=arguments,
        **kwargs,
    ).build_query()


def test_basic_building() -> None:
    """Standard builder usage with and without a model"""
    assert_query_equals(QueryBuilder(
        operation='query',
        method='findUnique',
        model='User',
        arguments={'where': {'id': '1'}}
    ), '''
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
      }
    }
    ''')
    assert_query_equals(QueryBuilder(
        operation='mutation',
        method='queryRaw',
        arguments={'where': {'id': '1'}}
    ), '''
    mutation {
      result: queryRaw
      (
        where: {
          id: "1"
        }
      )
    }
    ''')


def test_invalid_include() -> None:
    """Invalid include field raises error"""
    with pytest.raises(UnknownRelationalFieldError) as exception:
        QueryBuilder(
            operation='query',
            method='findUnique',
            model='User',
            arguments={
                'include': {
                    'hello': True,
                }
            }
        ).build_query()

    assert exception.match(
        'Field: "hello" either does not exist or is not a relational field on the User model'
    )


def test_include_no_model() -> None:
    """Trying to include a field without acess to a model raises an error"""
    with pytest.raises(ValueError) as exc:
        build_query(
            operation='mutation',
            method='queryRaw',
            arguments={'include': {'posts': True}}
        )

    assert exc.match('Cannot include fields when model is None.')


def test_include_with_arguments() -> None:
    """Including a field with filters"""
    assert_query_equals(QueryBuilder(
        operation='query',
        method='findUnique',
        model='User',
        arguments={
            'where': {'id': 1},
            'include': {'posts': {'where': {'id': 1}}}
        }
    ), '''
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
    }
    ''')


def test_raw_queries() -> None:
    """Raw queries serialise paramaters to JSON"""
    assert_query_equals(QueryBuilder(
        operation='mutation',
        method='queryRaw',
        arguments={
            'query': 'SELECT * FROM User where id = $1',
            'parameters': ["1263526"],
        }
    ), '''
    mutation {
      result: queryRaw
      (
        query: "SELECT * FROM User where id = $1"
        parameters: "[\\"1263526\\"]"
      )
    }
    ''')


def test_datetime_serialization_tz_aware(snapshot: SnapshotAssertion) -> None:
    """Serializing a timezone aware datetime converts to UTC"""
    query = QueryBuilder(
        operation='query',
        method='findUnique',
        model='Post',
        arguments={
            'where': {
                'created_at': datetime.datetime(1985, 10, 26, 1, 1, 1, tzinfo=datetime.timezone.max)
            }
        }
    ).build_query()
    assert query == snapshot


def test_datetime_serialization_tz_unaware(snapshot: SnapshotAssertion) -> None:
    """Serializing a timezone naive datetime converts to UTC"""
    query = QueryBuilder(
        operation='query',
        method='findUnique',
        model='Post',
        arguments={
            'where': {
                'created_at': datetime.datetime(1985, 10, 26, 1, 1, 1)
            }
        }
    ).build_query()
    assert query == snapshot


def test_unicode(snapshot: SnapshotAssertion) -> None:
    """Serializing unicode strings does not convert to ASCII"""
    query = QueryBuilder(
        operation='query',
        method='findUnique',
        model='User',
        arguments={
            'where': {
                'name': '❤',
            }
        }
    ).build_query()
    assert query == snapshot


def test_unknown_model() -> None:
    """Passing unknown model raises an error"""
    with pytest.raises(UnknownModelError) as exc:
        QueryBuilder(
            operation='query',
            method='findUnique',
            model='Foo',
            arguments={},
        ).build_query()

    assert exc.match(r'Model: "Foo" does not exist\.')


def test_unserializable_type() -> None:
    """Passing an unserializable type raises an error"""
    with pytest.raises(TypeError) as exc:
        QueryBuilder(
            operation='query',
            method='findFirst',
            arguments={
                'where': QueryBuilder
            }
        ).build_query()

    assert exc.match(r'Type <class \'prisma.builder.QueryBuilder\'> not serializable')


def test_unserializable_instance() -> None:
    """Passing an unserializable instance raises an error"""
    with pytest.raises(TypeError) as exc:
        QueryBuilder(
            operation='query',
            method='findFirst',
            arguments={
                'where': _NoneType()
            }
        ).build_query()

    assert exc.match(r'Type <class \'prisma.utils._NoneType\'> not serializable')


def test_custom_serialization(snapshot: SnapshotAssertion) -> None:
    """Registering a custom serializer serializes as expected"""
    class Foo:
        def __init__(self, arg: int) -> None:
            self.arg = arg

    @serializer.register(Foo)
    def custom_serializer(inst: Foo) -> int:  # pyright: reportUnusedFunction=false
        return inst.arg

    query = QueryBuilder(
        operation='query',
        method='findUnique',
        model='Post',
        arguments={
            'where': {
                'title': Foo(1),
            }
        }
    ).build_query()
    assert query == snapshot
