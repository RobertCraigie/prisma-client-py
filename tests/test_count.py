import pytest
from prisma import Client


# TODO: more tests


@pytest.mark.asyncio
async def test_count_no_results(client: Client) -> None:
    total = await client.post.count({'where': {'title': 'kdbsajdh'}})
    assert total == 0
