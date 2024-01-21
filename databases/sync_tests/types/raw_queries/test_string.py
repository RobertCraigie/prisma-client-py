from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Types

from ...._types import DatabaseMapping, SupportedDatabase
from ...._compat import LiteralString


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


def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of string in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = client.types.create({'string': 'abcd'})

    found = client.query_first(queries.select, 'abcd')
    assert found['id'] == record.id
    assert found['string'] == 'abcd'

    model = client.query_first(queries.select, 'abcd', model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.string == 'abcd'
