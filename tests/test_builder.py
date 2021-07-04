# fmt: off
# I prefer this way of formatting
from typing import Dict, Any

import pytest
from prisma.builder import QueryBuilder
from prisma.errors import UnknownRelationalFieldError

from .utils import assert_query_equals


# TODO: more tests
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
    with pytest.raises(ValueError) as exc:
        build_query(
            operation='mutation',
            method='queryRaw',
            arguments={'include': {'posts': True}}
        )

    assert exc.match('Cannot include fields when model is None.')


def test_include_with_arguments() -> None:
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
