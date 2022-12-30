import pytest
from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Types

from ...._compat import LiteralString
from ...._types import DatabaseMapping, SupportedDatabase


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Types WHERE string = ?',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE string = $1',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE string = ?',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of string in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = await client.types.create({'string': 'abcd'})

    found = await client.query_first(queries.select, 'abcd')
    assert found['id'] == record.id
    assert found['string'] == 'abcd'

    model = await client.query_first(queries.select, 'abcd', model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.string == 'abcd'


@pytest.mark.asyncio
async def test_raw_type(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """The runtime type when rich deserializing is not used"""
    queries = RAW_QUERIES[database]

    record = await client.types.create(
        {
            'string': 'kdjbfdjf',
        }
    )

    found = await client.query_first(
        queries.select,
        'kdjbfdjf',
        deserialize_types=False,
    )
    assert found['id'] == record.id
    assert found['string'] == 'kdjbfdjf'
