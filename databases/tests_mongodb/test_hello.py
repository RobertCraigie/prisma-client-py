import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_base_usage(client: Prisma) -> None:
    assert "Hello, World!" == "Hello, World!"
