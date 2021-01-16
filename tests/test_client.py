import pytest
from prisma import Client, errors


@pytest.mark.asyncio
async def test_catches_not_connected() -> None:
    client = Client()
    with pytest.raises(errors.ClientNotConnectedError) as exc:
        await client.post.delete_many()

    assert 'await client.connect()' in str(exc)
