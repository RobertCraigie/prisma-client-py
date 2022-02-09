import os
import time
import asyncio
import inspect
import logging
import warnings
import contextlib
from importlib.util import find_spec
from typing import Any, Union, Dict, Iterator, Coroutine, NoReturn

from ._types import FuncType, CoroType


def _env_bool(key: str) -> bool:
    return os.environ.get(key, '').lower() in {'1', 't', 'true'}


DEBUG = _env_bool('PRISMA_PY_DEBUG')
DEBUG_GENERATOR = _env_bool('PRISMA_PY_DEBUG_GENERATOR')
MAX_FN_SIGNATURE = 90


class _NoneType:  # pyright: reportUnusedClass=false
    def __bool__(self) -> bool:
        return False


def time_since(start: float, precision: int = 4) -> str:
    # TODO: prettier output
    delta = round(time.monotonic() - start, precision)
    return f'{delta}s'


def setup_logging() -> None:
    if DEBUG:
        logging.getLogger('prisma').setLevel(logging.DEBUG)


def maybe_async_run(func: Union[FuncType, CoroType], *args: Any, **kwargs: Any) -> Any:
    if is_coroutine(func):
        return async_run(func(*args, **kwargs))
    return func(*args, **kwargs)


# TODO: TypeVar return
def async_run(coro: Coroutine[Any, Any, Any]) -> Any:
    """Execute the coroutine and return the result."""
    return get_or_create_event_loop().run_until_complete(coro)


def is_coroutine(obj: Any) -> bool:
    return asyncio.iscoroutinefunction(obj) or inspect.isgeneratorfunction(obj)


def module_exists(name: str) -> bool:
    return find_spec(name) is not None


@contextlib.contextmanager
def temp_env_update(env: Dict[str, str]) -> Iterator[None]:
    old = os.environ.copy()

    try:
        os.environ.update(env)
        yield
    finally:
        for key in env:
            os.environ.pop(key, None)

        os.environ.update(old)


@contextlib.contextmanager
def monkeypatch(obj: Any, attr: str, new: Any) -> Any:
    """Temporarily replace a method with a new funtion

    The previously set method is passed as the first argument to the new function
    """

    def patched(*args: Any, **kwargs: Any) -> Any:
        return new(old, *args, **kwargs)

    old = getattr(obj, attr)

    try:
        setattr(obj, attr, patched)
        yield
    finally:
        setattr(obj, attr, old)


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """Return the currently set event loop or create a new event loop if there
    is no set event loop.

    Starting from python3.10, asyncio.get_event_loop() raises a DeprecationWarning
    when there is no event loop set, this deprecation will be enforced starting from
    python3.12

    This function serves as a future-proof wrapper over asyncio.get_event_loop()
    that preserves the old behaviour.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning)

        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop


def assert_never(value: NoReturn) -> NoReturn:
    """Used by type checkers for exhaustive match cases.

    https://github.com/microsoft/pyright/issues/767
    """
    assert False, "Unhandled type: {}".format(type(value).__name__)  # pragma: no cover


def fn_signature(func: FuncType) -> str:
    """Return the signature of a function."""

    base_sig = inspect.signature(func)
    params = dict(base_sig.parameters)
    if "self" in params:
        params.pop("self")

    base_signature = base_sig.replace(parameters=list(params.values()))
    short_str_signature = str(base_signature)
    short_str_signature = short_str_signature.replace("(", "", 1)
    if len(short_str_signature) > MAX_FN_SIGNATURE:
        short_str_signature = short_str_signature[0 : MAX_FN_SIGNATURE - 1] + '...'
    return short_str_signature
