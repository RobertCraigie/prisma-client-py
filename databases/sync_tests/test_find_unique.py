import pytest

from prisma import Prisma, errors


def test_find_unique_id_field(client: Prisma) -> None:
    """Finding a record by an ID field"""
    post = client.post.create(
        {
            'title': 'My post title!',
            'published': False,
        }
    )
    assert isinstance(post.id, str)

    found = client.post.find_unique(where={'id': post.id})
    assert found is not None
    assert found == post


def test_find_unique_missing_required_args(client: Prisma) -> None:
    """Missing field raises an error"""
    with pytest.raises(TypeError):
        client.post.find_unique()  # type: ignore[call-arg]

    # TODO: more constrained error type
    with pytest.raises(errors.DataError):
        client.post.find_unique(
            {
                'title': 'Hi from Prisma!',  # pyright: ignore
            }
        )


def test_find_unique_no_match(client: Prisma) -> None:
    """Looking for non-existent record does not error"""
    found = client.post.find_unique(where={'id': 'sjbsjahs'})
    assert found is None


def test_multiple_fields_are_not_allowed(client: Prisma) -> None:
    """Multiple fields cannot be passed at once"""
    with pytest.raises(errors.DataError):
        client.user.find_unique(
            where={
                'id': 'foo',
                'email': 'foo',  # type: ignore
            },
        )


def test_unique1(client: Prisma) -> None:
    """Standard combined unique constraint"""
    model = client.unique1.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )
    found = client.unique1.find_unique(
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


def test_unique2(client: Prisma) -> None:
    """Combined unique constraint with an aditional unique field"""
    model = client.unique2.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = client.unique2.find_unique(
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

    found = client.unique2.find_unique(
        where={
            'surname': 'Craigie',
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname


def test_unique3(client: Prisma) -> None:
    """Combined unique constraint with an ID field and a unique field"""
    model = client.unique3.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = client.unique3.find_unique(
        where={
            'name_surname': {
                'name': 'Robert',
                'surname': 'Craigie',
            },
        },
    )
    assert found is not None
    assert found.id == model.id

    found = client.unique3.find_unique(
        where={
            'surname': 'Craigie',
        },
    )
    assert found is not None
    assert found.id == model.id

    found = client.unique3.find_unique(
        where={
            'id': model.id,
        },
    )
    assert found is not None
    assert found.id == model.id


def test_unique4(client: Prisma) -> None:
    """Explicitly named unique constraint"""
    model = client.unique4.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = client.unique4.find_unique(
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


def test_unique5(client: Prisma) -> None:
    """Combined unique constraint with 3 fields"""
    model = client.unique5.create(
        data={
            'name': 'Robert',
            'middlename': 'Cosmo',
            'surname': 'Craigie',
        },
    )

    found = client.unique5.find_unique(
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


def test_id1(client: Prisma) -> None:
    """Standard combined ID constraint"""
    model = client.id1.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )
    found = client.id1.find_unique(
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


def test_id2(client: Prisma) -> None:
    """Combined ID constraint with a unique field"""
    model = client.id2.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = client.id2.find_unique(
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

    found = client.id2.find_unique(
        where={
            'surname': 'Craigie',
        },
    )
    assert found is not None
    assert found.name == model.name
    assert found.surname == model.surname


def test_id3(client: Prisma) -> None:
    """Explicitly named combined ID constraint"""
    model = client.id3.create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        },
    )

    found = client.id3.find_unique(
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


def test_id4(client: Prisma) -> None:
    """Combined ID constraint with 3 fields"""
    model = client.id4.create(
        data={
            'name': 'Robert',
            'middlename': 'Cosmo',
            'surname': 'Craigie',
        },
    )

    found = client.id4.find_unique(
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
