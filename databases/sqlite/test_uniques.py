from prisma import Prisma

# TODO: test json field


async def test_unique1(client: Prisma) -> None:
    """Standard combined unique constraint"""
    model = await client.unique1.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )
    found = await client.unique1.find_unique(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname


async def test_unique2(client: Prisma) -> None:
    """Combined unique constraint with an aditional unique field"""
    model = await client.unique2.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.unique2.find_unique(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname

    found = await client.unique2.find_unique(
        where={
            'surname': 'Craigie',
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname


async def test_unique3(client: Prisma) -> None:
    """Combined unique constraint with an ID field and a unique field"""
    model = await client.unique3.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.unique3.find_unique(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.id == model.id

    found = await client.unique3.find_unique(
        where={
            'surname': 'Craigie',
        },
    )
    assert found is not None
    assert found.id == model.id

    found = await client.unique3.find_unique(
        where={
            'id': model.id,
        },
    )
    assert found is not None
    assert found.id == model.id


async def test_unique4(client: Prisma) -> None:
    """Explicitly named unique constraint"""
    model = await client.unique4.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.unique4.find_unique(
        where={
            'my_unique': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname


async def test_unique5(client: Prisma) -> None:
    """Combined unique constraint with 3 fields"""
    model = await client.unique5.create(
        data={
            'name': 'Robert',
            'middlename': 'Cosmo',
            'surname': 'Craigie',
        },
    )

    found = await client.unique5.find_unique(
        where={
            'name_middlename_surname': {
                'name': 'Robert',
                'middlename': 'Cosmo',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.middlename == model.middlename
    assert found.surname == model.surname


async def test_id1(client: Prisma) -> None:
    """Standard combined ID constraint"""
    model = await client.id1.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )
    found = await client.id1.find_unique(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname


async def test_id2(client: Prisma) -> None:
    """Combined ID constraint with a unique field"""
    model = await client.id2.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.id2.find_unique(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname

    found = await client.id2.find_unique(
        where={
            'surname': 'Craigie',
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname


async def test_id3(client: Prisma) -> None:
    """Explicitly named combined ID constraint"""
    model = await client.id3.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.id3.find_unique(
        where={
            'my_id': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname


async def test_id4(client: Prisma) -> None:
    """Combined ID constraint with 3 fields"""
    model = await client.id4.create(
        data={
            'name': 'Robert',
            'middlename': 'Cosmo',
            'surname': 'Craigie',
        },
    )

    found = await client.id4.find_unique(
        where={
            'name_middlename_surname': {
                'name': 'Robert',
                'middlename': 'Cosmo',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.middlename == model.middlename
    assert found.surname == model.surname
