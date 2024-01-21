from decimal import Decimal

from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Types

from ...._types import DatabaseMapping, SupportedDatabase
from ...._compat import LiteralString


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Types WHERE decimal_ = ?',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE decimal_ = $1::numeric',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE decimal_ = ?',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
}


def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of decimal_ in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = client.types.create({'decimal_': Decimal(1)})

    found = client.query_first(queries.select, Decimal(1))
    assert found['id'] == record.id
    assert found['decimal_'] == 1

    record2 = client.types.create({'decimal_': Decimal('1.24343336464224')})

    found = client.query_first(queries.select, Decimal('1.24343336464224'))
    assert found['id'] == record2.id
    assert found['decimal_'] == 1.24343336464224

    model = client.query_first(queries.select, Decimal('1.24343336464224'), model=Types)
    assert model is not None
    assert model.id == record2.id
    assert model.decimal_ == Decimal('1.24343336464224')
