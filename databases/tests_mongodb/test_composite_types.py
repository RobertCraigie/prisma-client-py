import pytest

import prisma
from prisma import Prisma


@pytest.mark.asyncio
async def test_composite_type_create(client: Prisma) -> None:
    """
    Test creating a user with a composite type
    """
    user = await client.user.create({
        'name': 'Alice',
        'contact': {
            'email': 'alice@example.com',
            'phone': '123-456-7890'
        },
        'pets': []
    })

    assert user is not None
    assert user.id is not None
    assert user.name == 'Alice'


@pytest.mark.asyncio
async def test_composite_type_find_first_without_filters(client: Prisma) -> None:
    """
    Test finding a user with a composite type without any filters
    """
    await client.user.create({
        'name': 'Alice',
        'contact': {
            'email': 'alice@example.com',
            'phone': '123-456-7890'
        },
        'pets': []
    })

    user = await client.user.find_first()

    assert user is not None
    assert user.id is not None
    assert user.name == 'Alice'


@pytest.mark.asyncio
async def test_composite_type_without_complete_where(client: Prisma) -> None:
    """
    Test finding a user with a composite type without providing all the fields raises an error
    """
    await client.user.create({
        'name': 'Alice',
        'contact': {
            'email': 'alice@example.com',
            'phone': '123-456-7890'
        },
        'pets': []
    })

    with pytest.raises(prisma.errors.MissingRequiredValueError) as exc:
        await client.user.find_first(where={
            'contact': {
                'email': 'alice@example.com',
            },
        })
    
    assert '`where.contact.phone`: A value is required but not set' in str(exc.value)
    

@pytest.mark.asyncio
async def test_composite_type_with_complete_where(client: Prisma) -> None:
    """
    Test finding a user with a composite type with all the fields
    """
    await client.user.create({
        'name': 'Alice',
        'contact': {
            'email': 'alice@example.com',
            'phone': '123-456-7890'
        },
        'pets': []
    })

    user = await client.user.find_first(where={
        'contact': {
            'email': 'alice@example.com',
            'phone': '123-456-7890'
        },
    })

    assert user is not None
    assert user.id is not None
    assert user.name == 'Alice'


@pytest.mark.asyncio
async def test_composite_type_with_where_is(client: Prisma) -> None:
    """
    Test finding a user with a composite type with the `is` operator
    """
    await client.user.create({
        'name': 'Alice',
        'contact': {
            'email': 'alice@example.com',
            'phone': '123-456-7890'
        },
        'pets': []
    })

    user = await client.user.find_first(where={
        'contact': {
            'is': {
                'email': 'alice@example.com',
            }
        },
    })

    assert user is not None
    assert user.id is not None
    assert user.name == 'Alice'


@pytest.mark.asyncio
async def test_composite_type_with_where_equals_without_all_fields(client: Prisma) -> None:
    """
    Test finding a user with a composite type with the `equals` operator without all the fields
    """
    await client.user.create({
        'name': 'Alice',
        'contact': {
            'email': 'alice@example.com',
            'phone': '123-456-7890'
        },
        'pets': []
    })

    with pytest.raises(prisma.errors.MissingRequiredValueError) as exc:
        await client.user.find_first(where={
            'contact': {
                'equals': {
                    'email': 'alice@example.com',
                }
            },
        })

    assert '`where.contact.equals.phone`: A value is required but not set' in str(exc.value)


@pytest.mark.asyncio
async def test_composite_type_with_where_equals_with_all_fields(client: Prisma) -> None:
    """
    Test finding a user with a composite type with the `equals` operator with all the fields
    """
    await client.user.create({
        'name': 'Alice',
        'contact': {
            'email': 'alice@example.com',
            'phone': '123-456-7890'
        },
        'pets': []
    })

    user = await client.user.find_first(where={
        'contact': {
            'equals': {
                'email': 'alice@example.com',
                'phone': '123-456-7890'
            }
        },
    })

    assert user is not None
    assert user.id is not None
    assert user.name == 'Alice'
