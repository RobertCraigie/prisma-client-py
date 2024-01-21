import datetime

from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Types

from ...._types import DatabaseMapping, SupportedDatabase
from ...._compat import LiteralString


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


def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of a DateTime field in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    datetime_ = datetime.datetime(
        year=2022,
        month=12,
        day=25,
        hour=12,
        minute=1,
        second=34,
        tzinfo=datetime.timezone.utc,
    )

    record = client.types.create({'datetime_': datetime_})

    found = client.query_first(queries.select, record.id)
    assert found['id'] == record.id
    assert found['datetime_'] == '2022-12-25T12:01:34+00:00'

    model = client.query_first(queries.select, record.id, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.datetime_ == datetime_
