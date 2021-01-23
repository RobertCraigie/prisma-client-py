import os
import time
import asyncio
import inspect
import logging
from typing import Any, Union, Coroutine

from ._types import FuncType, CoroType


def time_since(start: float, precision: int = 4) -> str:
    # TODO: prettier output
    delta = round(time.monotonic() - start, precision)
    return f'{delta}s'


def setup_logging() -> None:
    if os.environ.get('PRISMA_PY_DEBUG'):
        logging.getLogger('prisma').setLevel(logging.DEBUG)


def maybe_async_run(func: Union[FuncType, CoroType], *args: Any, **kwargs: Any) -> Any:
    if is_coroutine(func):
        return async_run(func(*args, **kwargs))
    return func(*args, **kwargs)


def async_run(coro: Coroutine[Any, Any, Any]) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


def is_coroutine(obj: Any) -> bool:
    return asyncio.iscoroutinefunction(obj) or inspect.isgeneratorfunction(obj)
