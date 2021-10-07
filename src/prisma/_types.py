import sys
from typing import Callable, Coroutine, TypeVar, Any

from pydantic import BaseModel


if sys.version_info >= (3, 9):
    from typing import (  # pylint: disable=no-name-in-module, unused-import
        TypedDict as TypedDict,
        Protocol as Protocol,
        Literal as Literal,
        runtime_checkable as runtime_checkable,
    )
else:
    from typing_extensions import (
        TypedDict as TypedDict,
        Protocol as Protocol,
        Literal as Literal,
        runtime_checkable as runtime_checkable,
    )


Method = Literal['GET', 'POST']

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)

# TODO: use a TypeVar
FuncType = Callable[..., Any]
CoroType = Callable[..., Coroutine[Any, Any, Any]]
