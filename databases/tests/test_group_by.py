import pytest
from syrupy.assertion import SnapshotAssertion

import prisma
from prisma import Prisma
from lib.testing import async_fixture
from prisma.types import SortOrder

# TODO: test all types
# TODO: test working with the results


@async_fixture(autouse=True, scope='session')
async def create_test_data(client: Prisma) -> None:
    create = client.profile.create
    await create(
        {
            'description': 'from scotland',
            'country': 'Scotland',
            'city': 'Edinburgh',
            'views': 250,
            'user': {'create': {'name': 'Tegan'}},
        }
    )

    for _ in range(12):
        await create(
            {
                'description': 'description',
                'country': 'Denmark',
                'views': 500,
                'user': {'create': {'name': 'Robert'}},
            }
        )

    for _ in range(8):
        await create(
            {
                'description': 'description',
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
async def test_group_by(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Basic test grouping by 1 field with no additional filters"""
    assert (
        await client.user.group_by(
            ['name'],
            order={
                'name': 'asc',
            },
        )
        == snapshot
    )
    assert (
        await client.profile.group_by(
            ['country'],
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_docs_example(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Test the example given in the Prisma documentation:
    https://www.prisma.io/docs/reference/api-reference/prisma-client-reference#groupby
    """
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
async def test_order(snapshot: SnapshotAssertion, client: Prisma, order: SortOrder) -> None:
    """Test ordering results by a grouped field"""
    assert await client.profile.group_by(['country'], order={'country': order}) == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_order_list(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Test ordering results by a list of grouped fields"""
    results = await client.profile.group_by(
        by=['country', 'city'],
        order=[
            {'country': 'asc'},
            {'city': 'desc'},
        ],
    )
    # we have to apply this sorted operation as SQlite and PostgreSQL
    # have different default behaviour for sorting by nulls
    # and we don't support changing it yet
    results = sorted(results, key=lambda p: p.get('city') is not None)
    assert results == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_order_multiple_fields(client: Prisma) -> None:
    """Test ordering results by multiple fields is not support"""
    with pytest.raises(prisma.errors.DataError):
        await client.profile.group_by(
            ['country', 'city'],
            order={
                'city': 'desc',
                'country': 'asc',
            },
        )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_order_mismatched_arguments(client: Prisma) -> None:
    """The order argument only accepts fields that are being grouped"""
    with pytest.raises(prisma.errors.InputError) as exc:
        await client.profile.group_by(
            ['city'],
            order={  # pyright: ignore
                'country': 'asc',
            },
        )

    assert exc.match(
        r'Every field used for orderBy must be included in the by-arguments of the query\. ' r'Missing fields: country'
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
@pytest.mark.parametrize('order', ['asc', 'desc'])
async def test_take(
    snapshot: SnapshotAssertion,
    client: Prisma,
    order: SortOrder,
) -> None:
    """Take argument limits number of records returned"""
    assert (
        await client.profile.group_by(
            ['country'],
            take=1,
            order={'country': order},
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_take_missing_order_argument(client: Prisma) -> None:
    """The order argument must be provided to use take"""
    with pytest.raises(TypeError) as exc:
        await client.profile.group_by(['country'], take=1)

    assert exc.match("Missing argument: 'order' which is required when 'take' is present")


@pytest.mark.asyncio
@pytest.mark.persist_data
@pytest.mark.parametrize('order', ['asc', 'desc'])
async def test_skip(
    snapshot: SnapshotAssertion,
    client: Prisma,
    order: SortOrder,
) -> None:
    """Skipping grouped records"""
    assert (
        await client.profile.group_by(
            ['country'],
            skip=1,
            order={'country': order},
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_skip_missing_order_argument(client: Prisma) -> None:
    """The order argument must be provided to use skip"""
    with pytest.raises(TypeError) as exc:
        await client.profile.group_by(['country'], skip=1)

    assert exc.match("Missing argument: 'order' which is required when 'skip' is present")


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_where(client: Prisma) -> None:
    """Where argument correctly filters records"""
    results = await client.profile.group_by(
        ['country'],
        where={
            'country': 'Denmark',
        },
        order={
            'country': 'asc',
        },
    )
    assert len(results) == 1
    assert results[0].get('country') == 'Denmark'

    results = await client.profile.group_by(
        ['country'],
        where={
            'description': {
                'contains': 'scotland',
            },
        },
        order={
            'country': 'asc',
        },
    )
    assert len(results) == 1
    assert results[0].get('country') == 'Scotland'


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_having_missing_field_in_by(client: Prisma) -> None:
    """Having filters must be an aggregation filter or be included in by"""
    with pytest.raises(prisma.errors.InputError) as exc:
        await client.profile.group_by(
            by=['country'],
            count=True,
            having={
                'views': {
                    'gt': 50,
                },
            },
            order={
                'country': 'asc',
            },
        )

    assert exc.match(
        'Input error. Every field used in `having` filters must either be an aggregation filter '
        'or be included in the selection of the query. Missing fields: views'
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_having_aggregation(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Having aggregation filters records correctly"""
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
            order={
                'country': 'asc',
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
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_having_aggregation_nested(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Having aggregation filters nested within statements correctly filters records"""
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
        order={
            'country': 'asc',
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
        order={
            'country': 'asc',
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
        order={
            'country': 'asc',
        },
    )
    assert results == snapshot


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_count(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Counting records"""
    assert (
        await client.profile.group_by(
            ['country'],
            count=True,
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )
    assert (
        await client.profile.group_by(
            ['country'],
            count={
                '_all': True,
            },
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )
    assert (
        await client.profile.group_by(
            ['country'],
            count={
                'city': True,
            },
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )
    assert (
        await client.profile.group_by(
            ['country'],
            count={
                'city': True,
                'country': True,
            },
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_avg(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Getting the average of records"""
    assert (
        await client.profile.group_by(
            ['country'],
            avg={'views': True},
            order={'country': 'asc'},
        )
        == snapshot
    )
    assert (
        await client.types.group_by(
            ['string'],
            avg={'integer': True, 'bigint': True},
            order={'string': 'asc'},
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_sum(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Getting the sum of records"""
    assert (
        await client.profile.group_by(
            ['country'],
            sum={
                'views': True,
            },
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_min(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Getting the minimum value of records"""
    assert (
        await client.profile.group_by(
            ['country'],
            min={
                'views': True,
            },
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_max(snapshot: SnapshotAssertion, client: Prisma) -> None:
    """Getting the maximum value of records"""
    assert (
        await client.profile.group_by(
            ['country'],
            max={
                'views': True,
            },
            order={
                'country': 'asc',
            },
        )
        == snapshot
    )
