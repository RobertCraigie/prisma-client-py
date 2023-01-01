import pytest
from prisma import Prisma


@pytest.mark.asyncio
async def test_create_many(client: Prisma) -> None:
    """Standard usage"""
    total = await client.user.create_many(
        [{'name': 'Robert'}, {'name': 'Tegan'}]
    )
    assert total == 2

    user = await client.user.find_first(where={'name': 'Robert'})
    assert user is not None
    assert user.name == 'Robert'

    assert await client.user.count() == 2


@pytest.mark.asyncio
async def test_required_relation_key_field(client: Prisma) -> None:
    """Explicitly passing a field used as a foreign key connects the relations"""
    user = await client.user.create(
        data={
            'name': 'Robert',
        },
    )
    user2 = await client.user.create(
        data={
            'name': 'Robert',
        },
    )
    count = await client.profile.create_many(
        data=[
            {'user_id': user.id, 'description': 'Foo', 'country': 'Scotland'},
            {
                'user_id': user2.id,
                'description': 'Foo 2',
                'country': 'Scotland',
            },
        ],
    )
    assert count == 2

    found = await client.user.find_unique(
        where={
            'id': user.id,
        },
        include={
            'profile': True,
        },
    )
    assert found is not None
    assert found.profile is not None
    assert found.profile.description == 'Foo'

    found = await client.user.find_unique(
        where={
            'id': user2.id,
        },
        include={
            'profile': True,
        },
    )
    assert found is not None
    assert found.profile is not None
    assert found.profile.description == 'Foo 2'