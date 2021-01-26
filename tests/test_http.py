import pytest
from prisma.http import HTTP
from prisma.errors import HTTPClientClosedError


@pytest.mark.asyncio
async def test_request_on_closed_sessions() -> None:
    http = HTTP()
    assert http.closed is False
    await http.close()
    # assert http.closed is True

    with pytest.raises(HTTPClientClosedError):
        await http.request('GET', '/')
