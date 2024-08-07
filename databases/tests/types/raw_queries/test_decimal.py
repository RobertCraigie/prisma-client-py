from decimal import Decimal

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
    select='SELECT * FROM Types WHERE decimal_ = ?',
    select_null='SELECT * FROM Types WHERE optional_decimal IS NULL',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE decimal_ = $1::numeric',
    select_null='SELECT * FROM "Types" WHERE optional_decimal IS NULL',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE decimal_ = ?',
        select_null='SELECT * FROM Types WHERE optional_decimal IS NULL',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of decimal_ in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = await client.types.create({'decimal_': Decimal(1)})

    found = await client.query_first(queries.select, Decimal(1))
    assert found['id'] == record.id
    assert found['decimal_'] == 1

    record2 = await client.types.create({'decimal_': Decimal('1.24343336464224')})

    found = await client.query_first(queries.select, Decimal('1.24343336464224'))
    assert found['id'] == record2.id
    assert found['decimal_'] == 1.24343336464224

    model = await client.query_first(queries.select, Decimal('1.24343336464224'), model=Types)
    assert model is not None
    assert model.id == record2.id
    assert model.decimal_ == Decimal('1.24343336464224')


@pytest.mark.asyncio
async def test_query_first_optional(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Use of decimal in raw SELECT queries with optional/nullable results"""
    queries = RAW_QUERIES[database]

    record = await client.types.create({'optional_decimal': None})

    found = await client.query_first(queries.select_null)
    assert found['id'] == record.id
    assert found['optional_decimal'] is None

    model = await client.query_first(queries.select_null, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.optional_decimal is None
