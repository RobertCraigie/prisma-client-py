import pytest
from pydantic import BaseModel, Extra

from prisma import Prisma

from ...._compat import LiteralString
from ...._types import DatabaseMapping, SupportedDatabase
from ....utils import DatabaseConfig


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


class Model(BaseModel):
    id: int
    bool_: bool

    class Config(BaseModel.Config):
        extra: Extra = Extra.allow


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
    config: DatabaseConfig,
) -> None:
    """Support for disabling our rich parsing of types"""
    queries = RAW_QUERIES[database]

    record = await client.types.create({'bool_': True})

    found = await client.query_first(
        queries.select,
        True,
        deserialize_types=False,
    )
    assert found['id'] == record.id

    if config.bools_are_ints:
        assert found['bool_'] == 1
    else:
        assert found['bool_'] is True

    model = await client.query_first(
        queries.select,
        True,
        model=Model,
        deserialize_types=False,
    )
    assert model is not None
    assert model.id == record.id
    assert model.bool_ is True

    # sanity check to ensure the objects are destructured correctly
    dumped = model.json(indent=2)
    assert 'prisma__type' not in dumped
    assert 'prisma__value' not in dumped
