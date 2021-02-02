import sys
from typing import Callable, Coroutine, Any


if sys.version_info >= (3, 8):
    from typing import (  # pylint: disable=no-name-in-module, unused-import
        TypedDict,
        Literal,
    )
else:
    from typing_extensions import TypedDict, Literal


Method = Literal['GET', 'POST']

# TODO: use a TypeVar
FuncType = Callable[..., Any]
CoroType = Callable[..., Coroutine[Any, Any, Any]]
