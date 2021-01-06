import pytest
from prisma import Client
from prisma.engine import errors


@pytest.mark.asyncio
async def test_engine_connects() -> None:
    db = Client()
    await db.connect()

    with pytest.raises(errors.AlreadyConnectedError):
        await db.connect()

    await db.disconnect()
