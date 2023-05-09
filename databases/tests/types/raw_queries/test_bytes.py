from __future__ import annotations

import pytest
from pydantic import BaseModel

from prisma import Prisma, Base64
from prisma.models import Types

from ...._compat import LiteralString
from ...._types import DatabaseMapping, SupportedDatabase


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Types WHERE id = ?',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE id = $1',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE id = ?',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
    'sqlserver': Queries(
        select='SELECT * FROM Types WHERE id = @P1',
    ),
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of Bytes in raw SELECT queries"""
    queries = RAW_QUERIES[database]
    assert queries is not None

    record = await client.types.create({'bytes': Base64.encode(b'foo')})

    found = await client.query_first(queries.select, record.id)
    assert found is not None
    assert found['id'] == record.id
    assert found['bytes'] == 'Zm9v'

    model = await client.query_first(queries.select, record.id, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.bytes.decode_str() == 'foo'
