import contextlib

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from prisma import Client, errors, types
from prisma.actions import PostActions

from . import strategies


# TODO: don't send queries to query engine
# TODO: ensure all types are touched by hypothesis

strategies.register_type_for_models(
    'FindMany{model}ArgsFromPost',
    lambda t: strategies.from_typeddict(
        t, skip=st.from_type(int).filter(lambda i: i >= 0)
    ),
)

st.register_type_strategy(
    types.PostOrderByInput,
    strategies.from_typeddict(types.PostOrderByInput).filter(lambda v: len(v) <= 1),
)

from typing import Iterator


@contextlib.contextmanager
def ignore_known_errors() -> Iterator[None]:
    try:
        yield
    except (errors.RecordNotFoundError, errors.UniqueViolationError):
        # known errors that do not constitute an invalid GraphQL query
        # and are a result of missing / existing data
        pass
    except errors.RawQueryError as exc:
        # empty SQL query passed
        if exc.message == 'not an error':
            return

        # too many / few parameters passed
        if exc.message == 'N/A':
            return

        # SQL syntax error
        # TODO: generate valid SQL statements
        if exc.message.startswith('unrecognized token'):
            return
        if 'syntax error' in exc.message:
            return

        raise
    except errors.DataError as exc:
        value = str(exc)
        if 'Field does not exist on enclosing type' in value and value.endswith(
            '.not`'
        ):
            return

        if 'Invalid value for skip argument: Value can only be positive' in value:
            return

        if (
            'Input error. Unable to process combination of query arguments for aggregation query. Please note that it is not possible at the moment to have a null-cursor, or a cursor and orderBy combination that not stable (unique).'
            in value
        ):
            return

        raise exc


"""
from graphql import GraphQLSchema, GraphQLError, build_ast_schema, parse
from ariadne.graphql import parse_query, validate_query as validate_query_document

import re
from pathlib import Path
from typing import Callable, Union, Any

from prisma.builder import QueryBuilder


Validator = Callable[[str], None]


# NOTE: some of this is invalid due to commenting it out
ENUM_RE = re.compile(
     r' Enum \'\\w+\' cannot represent non-enum value: "(?P<actual>\\w+)"\\. Did you mean the enum value \'(?P<expected>\\w+)\'',
    re.DEBUG,
)


class CapturedQuery(Exception):
    def __init__(self, query: str) -> None:
        self.query = query


@contextlib.contextmanager
def capture_query(monkeypatch: 'TODO') -> Iterator[str]:
    def patched_build_query(*args: Any, **kwargs: Any) -> None:
        query = actual_build_query(*args, **kwargs)
        raise CapturedQuery(query)

    actual_build_query = QueryBuilder.build_query
    monkeypatch.setattr(QueryBuilder, 'build_query', patched_build_query, raising=True)
    cap = CapturedQuery(None)

    try:
        yield cap
    except CapturedQuery as exc:
        cap.query = exc.query


@pytest.fixture(name='schema', scope='session')
def schema_fixture() -> GraphQLSchema:
    # TODO: download this automatically
    content = (Path(__file__).parent.parent / 'scripts' / 'schema.gql').read_text()
    return build_ast_schema(parse(content))


@pytest.fixture(scope='session')
def validate_query(schema: GraphQLSchema) -> Validator:
    def validate(query: Union[str, CapturedQuery]) -> None:
        # print(query)
        assert query is not None
        if isinstance(query, CapturedQuery):
            query = query.query

        document = parse_query(query)
        errors = validate_query_document(schema, document)
        for error in errors:
            print(error)
            message = error.message

            if 'Enum' in message:
                print(bytes(message, 'utf-8'))

            match = ENUM_RE.match(message)
            if match is not None:
                # GraphQL python expects enum values to be unquoted but Prisma
                # expects quotes
                print('nice')
                if match.group('actual') == match.group('expected'):
                    continue

            raise error

        return

    return validate
"""


# TODO: test what types are touched by hypothesis
# TODO: remove health check suppression


@pytest.mark.asyncio
@given(data=strategies.from_method(Client.query_raw))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_query_raw(data: strategies.FromMethod, client: Client) -> None:
    query = data.kwargs.pop('query')

    with ignore_known_errors():
        assert isinstance(
            await client.query_raw(query, *data.args, **data.kwargs), data.returntype
        )


@pytest.mark.asyncio
@given(data=strategies.from_method(Client.query_first))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_query_first(data: strategies.FromMethod, client: Client) -> None:
    query = data.kwargs.pop('query')

    with ignore_known_errors():
        assert isinstance(
            await client.query_first(query, *data.args, **data.kwargs), data.returntype
        )


@pytest.mark.asyncio
@given(data=strategies.from_method(Client.execute_raw))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_execute_raw(data: strategies.FromMethod, client: Client) -> None:
    query = data.kwargs.pop('query')
    with ignore_known_errors():
        assert isinstance(
            await client.execute_raw(query, *data.args, **data.kwargs), data.returntype
        )


# strategies.from_method(PostActions.create)
# print(PostActions.create.__annotations__['data'].__annotations__)
# raise RuntimeError


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.create))
@settings(
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
)
async def test_create(
    data: strategies.FromMethod,
    client: Client,
) -> None:
    with ignore_known_errors():
        await client.post.create(*data.args, **data.kwargs)


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.delete))
@settings(
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
)
async def test_delete(
    data: strategies.FromMethod,
    client: Client,
) -> None:
    with ignore_known_errors():
        await client.post.delete(*data.args, **data.kwargs)


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.find_unique))
@settings(
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
)
async def test_find_unique(
    data: strategies.FromMethod,
    client: Client,
) -> None:
    with ignore_known_errors():
        await client.post.find_unique(*data.args, **data.kwargs)


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.find_many))
@settings(
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
)
async def test_find_many(
    data: strategies.FromMethod,
    client: Client,
) -> None:
    with ignore_known_errors():
        await client.post.find_many(*data.args, **data.kwargs)


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.find_first))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_find_first(data: strategies.FromMethod, client: Client) -> None:
    with ignore_known_errors():
        await client.post.find_first(*data.args, **data.kwargs)


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.update))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_update(data: strategies.FromMethod, client: Client) -> None:
    with ignore_known_errors():
        await client.post.update(*data.args, **data.kwargs)


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.upsert))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_upsert(data: strategies.FromMethod, client: Client) -> None:
    with ignore_known_errors():
        assert isinstance(
            await client.post.upsert(*data.args, **data.kwargs), data.returntype
        )


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.update_many))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_update_many(data: strategies.FromMethod, client: Client) -> None:
    with ignore_known_errors():
        assert isinstance(
            await client.post.update_many(*data.args, **data.kwargs), data.returntype
        )


# TODO: this test passes using Client().post.count
@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.count))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_count(data: strategies.FromMethod, client: Client) -> None:
    with ignore_known_errors():
        assert isinstance(
            await client.post.count(*data.args, **data.kwargs), data.returntype
        )


@pytest.mark.asyncio
@given(data=strategies.from_method(PostActions.delete_many))
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_delete_many(data: strategies.FromMethod, client: Client) -> None:
    with ignore_known_errors():
        assert isinstance(
            await client.post.delete_many(*data.args, **data.kwargs), data.returntype
        )


if __name__ == '__main__':
    print('\n'.join(dir(test_create)))
