import sys
from typing import Callable, Coroutine, TypeVar, Any

from pydantic import BaseModel


if sys.version_info >= (3, 8):
    from typing import (  # pylint: disable=no-name-in-module, unused-import
        TypedDict as TypedDict,
        Literal as Literal,
    )
else:
    from typing_extensions import (
        TypedDict as TypedDict,
        Literal as Literal,
    )


Method = Literal['GET', 'POST']

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)

# TODO: use a TypeVar
FuncType = Callable[..., Any]
CoroType = Callable[..., Coroutine[Any, Any, Any]]
