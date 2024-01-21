import json

import pytest
from pydantic import BaseModel

from prisma import Json, Prisma
from prisma.models import Types

from ...._types import DatabaseMapping, SupportedDatabase
from ...._compat import LiteralString


class Queries(BaseModel):
    select: LiteralString


_postgresql_queries = Queries(
    select='SELECT * FROM "Types" WHERE json_obj = $1',
)

RAW_QUERIES: DatabaseMapping[Queries] = {
    'mysql': Queries(
        select='SELECT * FROM Types WHERE json_obj->"$.foo" = ?',
    ),
    'mariadb': Queries(
        select="SELECT * FROM Types WHERE JSON_CONTAINS(json_obj, '\"bar\"', '$.foo')",
    ),
    'sqlite': Queries(
        select='SELECT * FROM Types WHERE json_obj = ?',
    ),
    'postgresql': _postgresql_queries,
    'cockroachdb': _postgresql_queries,
}


@pytest.mark.asyncio
async def test_query_first(
    client: Prisma,
    database: SupportedDatabase,
) -> None:
    """Standard usage of json_obj in raw SELECT queries"""
    queries = RAW_QUERIES[database]

    record = await client.types.create(
        {
            'json_obj': Json.keys(
                foo='bar',
                is_foo=True,
            )
        }
    )

    raw = {
        'foo': 'bar',
        'is_foo': True,
    }

    if database == 'mysql':
        # filtering by the full JSON object does not work for MySQL
        args = ['bar']
    elif database == 'mariadb':
        # I couldn't figure out the right syntax for passing query
        # parameters for this case in MariaDB
        args = []
    else:
        args = [raw]

    found = await client.query_first(queries.select, *args)
    assert found['id'] == record.id

    if database == 'mariadb':
        # MariaDB will return JSON fields as a raw string
        obj = json.loads(found['json_obj'])
    else:
        obj = found['json_obj']

    assert obj == raw
    assert obj['is_foo'] is True

    model = await client.query_first(queries.select, *args, model=Types)
    assert model is not None
    assert model.id == record.id
    assert model.json_obj is not None
    assert model.json_obj == raw
    assert model.json_obj['is_foo'] is True
