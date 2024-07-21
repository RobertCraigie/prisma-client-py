import pytest

from prisma import Prisma


@pytest.mark.asyncio()
async def test_querying(client: Prisma) -> None:
    user = await client.user.create({'name': 'robert', 'email': 'robert@craigie.dev'})
    assert isinstance(user.id, int)
    assert user.name == 'robert'
    assert user.email == 'robert@craigie.dev'
