import os
import time
import asyncio
import inspect
import logging
import contextlib
from importlib.util import find_spec
from typing import Any, Union, Dict, Iterator, Coroutine

from ._types import FuncType, CoroType


def _env_bool(key: str) -> bool:
    return os.environ.get(key, '').lower() in {'1', 't', 'true'}


DEBUG = _env_bool('PRISMA_PY_DEBUG')
DEBUG_GENERATOR = _env_bool('PRISMA_PY_DEBUG_GENERATOR')


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


def async_run(coro: Coroutine[Any, Any, Any]) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


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
        for key in env.keys():
            os.environ.pop(key, None)

        os.environ.update(old)
