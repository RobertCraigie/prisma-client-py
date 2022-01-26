import pytest
from prisma.models import Record, User


# TODO: Base64 and Bytes fields
# TODO: cleanup


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_update() -> None:
    """Updating scalar fields of a model"""
    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
    )
    assert user.name == 'Robert'
    user.name = 'Tegan'
    assert user.name == 'Tegan'

    updated = await user.record().update()

    print(updated.json(indent=2))
    assert user == updated


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_update_1_to_many() -> None:
    """Updating a One to Many relational field of a model"""
    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
        include={
            'posts': True,
        },
    )
    updated = await user.record().update()
    print(updated.json(indent=2))
    assert False


class MyUser(User, warn_subclass=False):
    foo: str = 'bar'


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_update_subclass() -> None:
    """Updating a model that has been subclassed"""
    user = await MyUser.prisma().create({'name': 'Robert'})
    assert user.name == 'Robert'

    user.foo = 'Wow'
    user.name = 'Tegan'
    assert user.name == 'Tegan'

    updated = await user.record().update()
    assert updated.id == user.id


@pytest.mark.asyncio
@pytest.mark.prisma
async def test_update_combined_unique_constraint() -> None:
    """Updating a model that uses a combined unique constraint"""
    record = await Record.prisma().create(
        data={
            'first': 'Foo',
            'last': 'Bar',
        },
    )
    record.first = 'Baz'
    updated = await record.record().update()
    assert updated.first == 'Baz'

    found = await Record.prisma().find_unique(
        where={
            'first_last': {
                'first': 'Baz',
                'last': 'Bar',
            },
        },
    )
    assert found is not None


# TODO: test relational fields
