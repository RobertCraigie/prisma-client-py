import pytest

from prisma import Prisma, errors


@pytest.mark.asyncio
async def test_id_field(client: Prisma) -> None:
    """Finding a record by an ID field"""
    post = await client.post.create(
        {
            'title': 'My post title!',
            'published': False,
        }
    )
    assert isinstance(post.id, str)

    found = await client.post.find_unique_or_raise(where={'id': post.id})
    assert found == post


@pytest.mark.asyncio
async def test_missing_required_args(client: Prisma) -> None:
    """Missing field raises an error"""
    with pytest.raises(TypeError):
        await client.post.find_unique_or_raise()  # type: ignore[call-arg]

    # TODO: more constrained error type
    with pytest.raises(errors.DataError):
        await client.post.find_unique_or_raise(
            {
                'title': 'Hi from Prisma!',  # pyright: ignore
            }
        )


@pytest.mark.asyncio
async def test_no_match(client: Prisma) -> None:
    """Looking for non-existent record raises an error"""
    with pytest.raises(
        errors.RecordNotFoundError,
        match=r'depends on one or more records that were required but not found',
    ):
        await client.post.find_unique_or_raise(where={'id': 'sjbsjahs'})


@pytest.mark.asyncio
async def test_multiple_fields_are_not_allowed(client: Prisma) -> None:
    """Multiple fields cannot be passed at once"""
    with pytest.raises(errors.DataError):
        await client.user.find_unique_or_raise(
            where={
                'id': 'foo',
                'email': 'foo',  # type: ignore
            },
        )


@pytest.mark.asyncio
async def test_unique1(client: Prisma) -> None:
    """Standard combined unique constraint"""
    model = await client.unique1.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )
    found = await client.unique1.find_unique_or_raise(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found.name == model.name
    assert found.surname == model.surname


@pytest.mark.asyncio
async def test_unique2(client: Prisma) -> None:
    """Combined unique constraint with an aditional unique field"""
    model = await client.unique2.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.unique2.find_unique_or_raise(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found.name == model.name
    assert found.surname == model.surname

    found = await client.unique2.find_unique_or_raise(
        where={
            'surname': 'Craigie',
        },
    )
    assert found.name == model.name
    assert found.surname == model.surname


@pytest.mark.asyncio
async def test_unique3(client: Prisma) -> None:
    """Combined unique constraint with an ID field and a unique field"""
    model = await client.unique3.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.unique3.find_unique_or_raise(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found.id == model.id

    found = await client.unique3.find_unique_or_raise(
        where={
            'surname': 'Craigie',
        },
    )
    assert found.id == model.id

    found = await client.unique3.find_unique_or_raise(
        where={
            'id': model.id,
        },
    )
    assert found.id == model.id


@pytest.mark.asyncio
async def test_unique4(client: Prisma) -> None:
    """Explicitly named unique constraint"""
    model = await client.unique4.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.unique4.find_unique_or_raise(
        where={
            'my_unique': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found.name == model.name
    assert found.surname == model.surname


@pytest.mark.asyncio
async def test_unique5(client: Prisma) -> None:
    """Combined unique constraint with 3 fields"""
    model = await client.unique5.create(
        data={
            'name': 'Robert',
            'middlename': 'Cosmo',
            'surname': 'Craigie',
        },
    )

    found = await client.unique5.find_unique_or_raise(
        where={
            'name_middlename_surname': {
                'name': 'Robert',
                'middlename': 'Cosmo',
                'surname': 'Craigie',
            },
        },
    )
    assert found.name == model.name
    assert found.middlename == model.middlename
    assert found.surname == model.surname


@pytest.mark.asyncio
async def test_id1(client: Prisma) -> None:
    """Standard combined ID constraint"""
    model = await client.id1.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )
    found = await client.id1.find_unique_or_raise(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found.name == model.name
    assert found.surname == model.surname


@pytest.mark.asyncio
async def test_id2(client: Prisma) -> None:
    """Combined ID constraint with a unique field"""
    model = await client.id2.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.id2.find_unique_or_raise(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found.name == model.name
    assert found.surname == model.surname

    found = await client.id2.find_unique_or_raise(
        where={
            'surname': 'Craigie',
        },
    )
    assert found.name == model.name
    assert found.surname == model.surname


@pytest.mark.asyncio
async def test_id3(client: Prisma) -> None:
    """Explicitly named combined ID constraint"""
    model = await client.id3.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = await client.id3.find_unique_or_raise(
        where={
            'my_id': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found.name == model.name
    assert found.surname == model.surname


@pytest.mark.asyncio
async def test_id4(client: Prisma) -> None:
    """Combined ID constraint with 3 fields"""
    model = await client.id4.create(
        data={
            'name': 'Robert',
            'middlename': 'Cosmo',
            'surname': 'Craigie',
        },
    )

    found = await client.id4.find_unique_or_raise(
        where={
            'name_middlename_surname': {
                'name': 'Robert',
                'middlename': 'Cosmo',
                'surname': 'Craigie',
            },
        },
    )
    assert found.name == model.name
    assert found.middlename == model.middlename
    assert found.surname == model.surname
