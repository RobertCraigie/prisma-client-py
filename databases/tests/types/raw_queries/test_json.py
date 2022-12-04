import pytest
from pydantic import BaseModel

from prisma import Prisma, Json
from prisma.models import Types

from ...._compat import LiteralString
from ...._types import DatabaseMapping, SupportedDatabase


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Types WHERE json_obj->"$.foo" = ?',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE json_obj = $1',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE json_obj = ?',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of json_obj in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = await client.types.create(
        {
            'json_obj': Json.keys(
                foo='bar',
                is_foo=True,
            )
        }
    )

    raw = {
        'foo': 'bar',
        'is_foo': True,
    }

    if database in ['mysql', 'mariadb']:
        # filtering by the full JSON object does not work for MySQL-like DBs
        arg = 'bar'
    else:
        arg = raw

    found = await client.query_first(queries.select, arg)
    assert found['id'] == record.id
    assert found['json_obj'] == raw
    assert found['json_obj']['is_foo'] is True

    model = await client.query_first(queries.select, arg, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.json_obj is not None
    assert model.json_obj == raw
    assert model.json_obj['is_foo'] is True
