# fmt: off
# I prefer this way of formatting
import functools
from typing import Any

import pytest
from prisma.builder import QueryBuilder
from prisma.utils import _env_bool
from prisma.errors import UnknownRelationalFieldError

from .utils import Testdir, assert_query_equals


# TODO: more tests
# TODO: these tests should be schema agnostic
#       one schema should be used for all these tests
#       and only changed when needed for these tests
#       otherwise, simply adding a field to a model
#       will break these tests


def build_query(**kwargs: Any) -> str:
    return QueryBuilder(**kwargs).build_query()


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
    builder = functools.partial(QueryBuilder, operation='query', method='findUnique', model='User')
    with pytest.raises(TypeError) as exc:
        builder(arguments={'include': 1}).build_query()

    assert exc.match('Expected `dict` include value but got type=<class \'int\'> instead')

    with pytest.raises(UnknownRelationalFieldError) as exception:
        builder(arguments={'include': {'hello': True}}).build_query()

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
          createdAt
          updatedAt
          title
          published
          views
          desc
          authorId
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


@pytest.mark.skipif(
    not _env_bool('PRISMA_PY_TEST_BUGS'),
    reason='This is a known bug'
)
def test_aliases_edge_case(testdir: Testdir) -> None:
    def tests() -> None:  # pylint: disable=all
        from prisma.builder import QueryBuilder
        from tests.utils import assert_query_equals

        def test_aliases_edge_case() -> None:
            builder = QueryBuilder(
                method='upsertOne',
                operation='mutation',
                model='User',
                arguments={
                    'where': {
                        'id': 1
                    },
                    'create': {
                        'my_field': 'Robert',
                        'my_create_field': 'foo',
                    },
                    'update': {
                        'my_field': 'Robert',
                        'my_create_field': 'foo',
                    },
                }
            )
            assert_query_equals((
                builder
            ), '''
            mutation {
              result: upsertOneUser
              (
                where: {
                  id: 1
                }
                create: {
                  myField: "Robert"
                  my_create_field: "foo"
                }
                update: {
                  myField: "Robert"
                  my_create_field: "foo"
                }
              )
              {
                id
                myField
                create_model_id
              }
            }
            ''')

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
            id              Int         @id
            myField         String
            create          CreateModel @relation(fields: [create_model_id], references: [id])
            create_model_id Int
        }}

        model CreateModel {{
            id            Int    @id
            myCreateField String
            user          User?
        }}
    '''
    testdir.generate(schema=schema)
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=1)
