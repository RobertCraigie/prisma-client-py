import pytest
from prisma.models import User

from ..utils import RawQueries


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_query_raw(raw_queries: RawQueries) -> None:
    """Ensure results are transformed to the expected BaseModel"""
    users = [
        await User.prisma().create({'name': 'Robert'}),
        await User.prisma().create({'name': 'Tegan'}),
    ]
    results = await User.prisma().query_raw(
        raw_queries.find_user_by_id,
        users[1].id,
    )
    assert len(results) == 1
    assert results[0].name == 'Tegan'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_query_first(raw_queries: RawQueries) -> None:
    """Ensure results are transformed to the expected BaseModel"""
    users = [
        await User.prisma().create({'name': 'Robert'}),
        await User.prisma().create({'name': 'Tegan'}),
    ]
    user = await User.prisma().query_first(
        raw_queries.find_user_by_id_limit_1, users[1].id
    )
    assert user is not None
    assert user.name == 'Tegan'
