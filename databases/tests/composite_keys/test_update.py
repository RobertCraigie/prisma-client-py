import pytest
from prisma.models import Unique2


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_update_unique_field() -> None:
    """Setting a unique field"""
    record = await Unique2.prisma().create(
        data={
            'name': 'Robert',
            'surname': 'Craigie',
        }
    )

    updated = await Unique2.prisma().update(
        where={
            'surname': record.surname,
        },
        data={
            'surname': 'George',
        },
    )
    assert updated is not None
    assert updated.name == record.name
    assert updated.surname == 'George'
