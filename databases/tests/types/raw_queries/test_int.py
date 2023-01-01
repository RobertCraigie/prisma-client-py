from __future__ import annotations

import pytest
from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Types

from ...._compat import LiteralString
from ...._types import DatabaseMapping, SupportedDatabase


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Types WHERE `integer` = ?',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE integer = $1',
)

RAW_QUERIES: DatabaseMapping[Queries | None] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE integer = ?',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
    # TODO
    'sqlserver': None,
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of integer in raw SELECT queries"""
    queries = RAW_QUERIES[database]
    assert queries is not None

    record = await client.types.create({'integer': 12522})

    found = await client.query_first(queries.select, 12522)
    assert found['id'] == record.id
    assert found['integer'] == 12522

    model = await client.query_first(queries.select, 12522, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.integer == 12522