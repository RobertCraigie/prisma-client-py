import pytest
from pydantic import BaseModel

from prisma import Base64, Prisma
from prisma.models import Types

from ...._types import DatabaseMapping, SupportedDatabase
from ...._compat import LiteralString


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
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of Bytes in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = await client.types.create({'bytes': Base64.encode(b'foo')})

    found = await client.query_first(queries.select, record.id)
    assert found is not None
    assert found['id'] == record.id
    assert found['bytes'] == 'Zm9v'

    model = await client.query_first(queries.select, record.id, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.bytes.decode_str() == 'foo'
