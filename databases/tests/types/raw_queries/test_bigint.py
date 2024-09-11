import pytest
from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Types

from ...._types import DatabaseMapping, SupportedDatabase
from ...._compat import LiteralString


class Queries(BaseModel):
    select: LiteralString
    select_null: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Types WHERE `bigint` = ?',
    select_null='SELECT * FROM Types WHERE `optional_bigint` IS NULL',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE bigint = $1',
    select_null='SELECT * FROM "Types" WHERE optional_bigint IS NULL',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE bigint = ?',
        select_null='SELECT * FROM Types WHERE optional_bigint IS NULL',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of BigInt in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = await client.types.create({'bigint': 12522})

    found = await client.query_first(queries.select, 12522)
    assert found['id'] == record.id
    assert found['bigint'] == 12522

    model = await client.query_first(queries.select, 12522, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.bigint == 12522


@pytest.mark.asyncio
async def test_query_first_optional(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Use of BigInt in raw SELECT queries with optional/nullable results"""
    queries = RAW_QUERIES[database]

    record = await client.types.create({'optional_bigint': None})

    found = await client.query_first(queries.select_null)
    assert found['id'] == record.id
    assert found['optional_bigint'] is None

    model = await client.query_first(queries.select_null, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.optional_bigint is None
