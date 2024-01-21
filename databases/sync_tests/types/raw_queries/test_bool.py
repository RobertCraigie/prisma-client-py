from pydantic import BaseModel

from prisma import Prisma
from prisma.models import Types

from ....utils import DatabaseConfig
from ...._types import DatabaseMapping, SupportedDatabase
from ...._compat import LiteralString


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Types WHERE bool_ = ?',
)

_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE bool_ = $1',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': _mysql_queries,
    'mariadb': _mysql_queries,
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE bool_ = ?',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
}


def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
    config: DatabaseConfig,
) -> None:
    """Standard usage of Boolean in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = client.types.create({'bool_': True})

    found = client.query_first(queries.select, True)
    assert found['id'] == record.id

    if config.bools_are_ints:
        assert found['bool_'] == 1
    else:
        assert found['bool_'] is True

    model = client.query_first(queries.select, True, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.bool_ is True
