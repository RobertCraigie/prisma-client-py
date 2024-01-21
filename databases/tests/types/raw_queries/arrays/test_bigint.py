import pytest
from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Lists

from ....._types import DatabaseMapping, SupportedDatabase
from ....._compat import LiteralString


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Lists WHERE `id` = ?',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Lists" WHERE id = $1',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Lists WHERE id = ?',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of BigInt[] in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = await client.lists.create({'bigints': [12522]})

    found = await client.query_first(queries.select, record.id)
    assert found['id'] == record.id
    assert found['bigints'] == [12522]

    model = await client.query_first(queries.select, record.id, model=Lists)
    assert model is not None
    assert model.id == record.id
    assert model.bigints == [12522]
