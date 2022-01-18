import pytest
from prisma.models import User


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


# TODO: test relational fields
