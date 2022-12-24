import datetime

import pytest
from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Types

from ...._compat import LiteralString
from ...._types import DatabaseMapping, SupportedDatabase


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Types WHERE `id` = ?',
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
    """Standard usage of a DateTime @db.Date field in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    date = datetime.datetime(year=2022, month=12, day=25)

    record = await client.types.create({'date': date})

    found = await client.query_first(queries.select, record.id)
    assert found['id'] == record.id
    if database in {'mysql', 'mariadb'}:
        assert found['date'].replace(tzinfo=None) == date
    else:
        assert found['date'] == date

    model = await client.query_first(queries.select, record.id, model=Types)
    assert model is not None
    assert model.id == record.id
    if database in {'mysql', 'mariadb'}:
        assert model.date.replace(tzinfo=None) == date
    else:
        assert model.date == date


@pytest.mark.asyncio
async def test_raw_type(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """The runtime type when rich deserializing is not used"""
    queries = RAW_QUERIES[database]

    date_input = datetime.datetime(
        year=2022,
        month=12,
        day=25,
        tzinfo=datetime.timezone.utc,
    )

    record = await client.types.create({'date': date_input})

    found = await client.query_first(
        queries.select,
        record.id,
        deserialize_types=False,
    )
    assert found['id'] == record.id

    # some databases use slightly different representations, this doesn't really matter for our case
    if database in {'mysql', 'mariadb'}:
        assert found['date'] == '2022-12-25T00:00:00+00:00'
    else:
        assert found['date'] == '2022-12-25'
