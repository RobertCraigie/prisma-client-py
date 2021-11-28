from typing import cast

import pytest
import httpx
from prisma.http import HTTP
from prisma._types import Literal
from prisma.utils import _NoneType
from prisma.errors import HTTPClientClosedError


State = Literal['initial', 'open', 'closed']


def assert_session_state(http: HTTP, state: State) -> None:
    # pylint: disable=protected-access
    if state == 'initial':
        assert http._session is _NoneType
    elif state == 'open':
        assert isinstance(http._session, httpx.AsyncClient)
    elif state == 'closed':
        with pytest.raises(HTTPClientClosedError):
            assert http.session
    else:  # pragma: no cover
        raise ValueError(
            f'Unknown value {state} for state, must be one of initial, open or closed'
        )


@pytest.mark.asyncio
async def test_request_on_closed_sessions() -> None:
    """Attempting to make a request on a closed session raises an error"""
    http = HTTP()
    assert http.closed is False
    await http.close()

    # mypy thinks that http.closed is Literal[False]
    # when it is in fact a bool
    closed = cast(bool, http.closed)  # pyright: reportUnnecessaryCast = false
    assert closed is True

    with pytest.raises(HTTPClientClosedError):
        await http.request('GET', '/')


@pytest.mark.asyncio
async def test_lazy_session_open() -> None:
    """Accessing the session property opens the session"""
    http = HTTP()
    assert_session_state(http, 'initial')

    # access the session property, opening the session
    # TODO: test using an actual request
    assert http.session

    assert_session_state(http, 'open')
    await http.close()
    assert_session_state(http, 'closed')
