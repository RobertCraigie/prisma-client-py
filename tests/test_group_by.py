import pytest
from syrupy.assertion import SnapshotAssertion

import prisma
from prisma import Client
from prisma.types import SortOrder

from .utils import async_fixture


# TODO: test all types
# TODO: test working with the results


@async_fixture(autouse=True, scope='session')
async def create_test_data(client: Client) -> None:
    create = client.profile.create
    await create(
        {
            'bio': 'from scotland',
            'country': 'Scotland',
            'city': 'Edinburgh',
            'views': 250,
            'user': {'create': {'name': 'Tegan'}},
        }
    )

    for _ in range(12):
        await create(
            {
                'bio': 'bio',
                'country': 'Denmark',
                'views': 500,
                'user': {'create': {'name': 'Robert'}},
            }
        )

    for _ in range(8):
        await create(
            {
                'bio': 'bio',
                'country': 'Denmark',
                'city': 'Copenhagen',
                'views': 1000,
                'user': {'create': {'name': 'Robert'}},
            }
        )

    types_create = client.types.create
    for i in range(10):
        await types_create(
            {
                'integer': i,
            },
        )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_group_by(snapshot: SnapshotAssertion, client: Client) -> None:
    assert await client.user.group_by(['name']) == snapshot
    assert await client.profile.group_by(['country']) == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_docs_example(snapshot: SnapshotAssertion, client: Client) -> None:
    # https://www.prisma.io/docs/reference/api-reference/prisma-client-reference#groupby
    results = await client.profile.group_by(
        by=['country', 'city'],
        count={
            '_all': True,
            'city': True,
        },
        sum={
            'views': True,
        },
        order={
            'country': 'desc',
        },
        having={
            'views': {
                '_avg': {
                    'gt': 200,
                },
            },
        },
    )
    assert results == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
@pytest.mark.parametrize('order', ['asc', 'desc'])
async def test_order(
    snapshot: SnapshotAssertion, client: Client, order: SortOrder
) -> None:
    assert (
        await client.profile.group_by(['country'], order={'country': order}) == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
@pytest.mark.parametrize('order', ['asc', 'desc'])
async def test_take(
    snapshot: SnapshotAssertion, client: Client, order: SortOrder
) -> None:
    assert (
        await client.profile.group_by(['country'], take=1, order={'country': order})
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_take_missing_order_argument(client: Client) -> None:
    with pytest.raises(TypeError) as exc:
        await client.profile.group_by(['country'], take=1)

    assert exc.match(
        'Missing argument: \'order\' which is required when \'take\' is present'
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
@pytest.mark.parametrize('order', ['asc', 'desc'])
async def test_skip(
    snapshot: SnapshotAssertion, client: Client, order: SortOrder
) -> None:
    assert (
        await client.profile.group_by(['country'], skip=1, order={'country': order})
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_skip_missing_order_argument(client: Client) -> None:
    with pytest.raises(TypeError) as exc:
        await client.profile.group_by(['country'], skip=1)

    assert exc.match(
        'Missing argument: \'order\' which is required when \'skip\' is present'
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_where(client: Client) -> None:
    results = await client.profile.group_by(['country'], where={'country': 'Denmark'})
    assert len(results) == 1
    assert results[0].get('country') == 'Denmark'

    results = await client.profile.group_by(
        ['country'], where={'bio': {'contains': 'scotland'}}
    )
    assert len(results) == 1
    assert results[0].get('country') == 'Scotland'


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_having_missing_field_in_by(client: Client) -> None:
    with pytest.raises(prisma.errors.InputError) as exc:
        await client.profile.group_by(
            by=['country'], count=True, having={'views': {'gt': 50}}
        )

    assert exc.match(
        'Input error. Every field used in `having` filters must either be an aggregation filter '
        'or be included in the selection of the query. Missing fields: views'
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_having_aggregation(snapshot: SnapshotAssertion, client: Client) -> None:
    assert (
        await client.profile.group_by(
            by=['country'],
            count=True,
            having={
                'views': {
                    '_avg': {
                        'gt': 600,
                    }
                }
            },
        )
        == snapshot
    )
    assert (
        await client.profile.group_by(
            by=['country'],
            count=True,
            having={
                'views': {
                    '_avg': {
                        'lt': 600,
                    }
                }
            },
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_having_aggregation_nested(
    snapshot: SnapshotAssertion, client: Client
) -> None:
    results = await client.profile.group_by(
        by=['country'],
        count=True,
        having={
            'OR': [
                {
                    'views': {
                        '_avg': {
                            'equals': 1000,
                        },
                    },
                },
                {
                    'views': {
                        '_sum': {
                            'equals': 250,
                        },
                    },
                },
            ],
        },
    )
    assert results == snapshot

    results = await client.profile.group_by(
        by=['country'],
        count=True,
        having={
            'OR': [
                {
                    'views': {
                        '_avg': {
                            'equals': 700,
                        },
                    },
                },
                {
                    'views': {
                        '_sum': {
                            'equals': 250,
                        },
                    },
                },
            ],
        },
    )
    assert results == snapshot

    results = await client.profile.group_by(
        by=['country'],
        count=True,
        having={
            'OR': [
                {
                    'views': {
                        '_avg': {
                            'equals': 700,
                        },
                    },
                },
                {
                    'views': {
                        '_sum': {
                            'equals': 250,
                        },
                    },
                    'NOT': [
                        {
                            'views': {
                                '_min': {
                                    'equals': 250,
                                },
                            },
                        },
                    ],
                },
            ],
        },
    )
    assert results == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_count(snapshot: SnapshotAssertion, client: Client) -> None:
    assert await client.profile.group_by(['country'], count=True) == snapshot
    assert await client.profile.group_by(['country'], count={'_all': True}) == snapshot
    assert await client.profile.group_by(['country'], count={'city': True}) == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_avg(snapshot: SnapshotAssertion, client: Client) -> None:
    assert await client.profile.group_by(['country'], avg={'views': True}) == snapshot
    assert (
        await client.types.group_by(['string'], avg={'integer': True, 'bigint': True})
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_sum(snapshot: SnapshotAssertion, client: Client) -> None:
    assert await client.profile.group_by(['country'], sum={'views': True}) == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_min(snapshot: SnapshotAssertion, client: Client) -> None:
    assert await client.profile.group_by(['country'], min={'views': True}) == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_max(snapshot: SnapshotAssertion, client: Client) -> None:
    assert await client.profile.group_by(['country'], max={'views': True}) == snapshot
