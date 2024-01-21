from typing import TYPE_CHECKING, cast

import httpx
import pytest

from prisma.http import HTTP
from prisma.utils import _NoneType
from prisma._types import Literal
from prisma.errors import HTTPClientClosedError

from .utils import patch_method

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


State = Literal['initial', 'open', 'closed']


def assert_session_state(http: HTTP, state: State) -> None:
    if state == 'initial':
        assert http._session is _NoneType
    elif state == 'open':
        assert isinstance(http._session, httpx.AsyncClient)
    elif state == 'closed':
        with pytest.raises(HTTPClientClosedError):
            assert http.session
    else:  # pragma: no cover
        raise ValueError(f'Unknown value {state} for state, must be one of initial, open or closed')


@pytest.mark.asyncio
async def test_request_on_closed_sessions() -> None:
    """Attempting to make a request on a closed session raises an error"""
    http = HTTP()
    http.open()
    assert http.closed is False
    await http.close()

    # mypy thinks that http.closed is Literal[False]
    # when it is in fact a bool
    closed = cast(bool, http.closed)
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


@pytest.mark.asyncio
async def test_httpx_default_config(monkeypatch: 'MonkeyPatch') -> None:
    """The default timeout is passed to HTTPX"""
    http = HTTP()
    assert_session_state(http, 'initial')

    getter = patch_method(monkeypatch, httpx.AsyncClient, '__init__')

    http.open()
    assert_session_state(http, 'open')

    # hardcode the default config to ensure there are no unintended changes
    captured = getter()
    assert captured == (
        (),
        {
            'limits': httpx.Limits(max_connections=1000),
            'timeout': httpx.Timeout(30),
        },
    )
