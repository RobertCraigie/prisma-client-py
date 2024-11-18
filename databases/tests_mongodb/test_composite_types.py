import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_composite_types(client: Prisma) -> None:
    await client.user.create({'name': 'Alice', 'contact': {'email': 'test@test.com', 'phone': '123-456-7890'}})
    user = await client.user.find_first()

    assert user is not None
    assert user.name == 'Alice'
