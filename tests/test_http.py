from typing import cast

import pytest
from prisma.http import HTTP
from prisma.errors import HTTPClientClosedError


# TODO: test every HTTP library


@pytest.mark.asyncio
async def test_request_on_closed_sessions() -> None:
    http = HTTP()
    assert http.closed is False
    await http.close()

    # mypy thinks that http.closed is Literal[False]
    # when it is in fact a bool
    closed = cast(bool, http.closed)
    assert closed is True

    with pytest.raises(HTTPClientClosedError):
        await http.request('GET', '/')
