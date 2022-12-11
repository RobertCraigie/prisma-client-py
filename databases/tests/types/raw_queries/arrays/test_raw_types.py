from typing import List

import pytest
from pydantic import BaseModel, Extra

from prisma import Prisma

from ....._compat import LiteralString
from ....._types import DatabaseMapping, SupportedDatabase
from .....utils import DatabaseConfig


class Queries(BaseModel):
    select: LiteralString


_mysql_queries = Queries(
    select='SELECT * FROM Lists WHERE id = ?',
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


class Model(BaseModel):
    id: str
    bools: List[bool]

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

    record = await client.lists.create({'bools': [True, False]})

    found = await client.query_first(
        queries.select,
        record.id,
        deserialize_types=False,
    )
    assert found['id'] == record.id

    if config.bools_are_ints:
        assert found['bools'] == [1, 0]
    else:
        assert found['bools'] == [True, False]

    model = await client.query_first(
        queries.select,
        record.id,
        model=Model,
        deserialize_types=False,
    )
    assert model is not None
    assert model.id == record.id
    assert model.bools == [True, False]

    # sanity check to ensure the objects are destructured correctly
    dumped = model.json(indent=2)
    assert 'prisma__type' not in dumped
    assert 'prisma__value' not in dumped
