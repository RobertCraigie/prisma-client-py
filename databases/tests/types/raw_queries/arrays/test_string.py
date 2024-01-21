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
    """Standard usgae of String[] value in raw queries"""
    models = [
        await client.lists.create({}),
        await client.lists.create(
            data={
                'strings': ['a', 'b', 'c'],
            },
        ),
    ]
    queries = RAW_QUERIES[database]

    model = await client.query_first(queries.select, models[0].id, model=Lists)
    assert model is not None
    assert model.strings == []

    model = await client.query_first(queries.select, models[1].id, model=Lists)
    assert model is not None
    assert model.strings == ['a', 'b', 'c']

    found = await client.query_first(queries.select, models[1].id)
    assert found is not None
    assert found['strings'] == ['a', 'b', 'c']

    # checks what the behaviour is for empty arrays
    assert found['ints'] is None
