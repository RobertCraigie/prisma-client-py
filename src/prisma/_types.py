from typing import Callable, Coroutine, TypeVar, Any
from typing_extensions import (
    TypedDict as TypedDict,
    Protocol as Protocol,
    Literal as Literal,
    runtime_checkable as runtime_checkable,
)

from pydantic import BaseModel


Method = Literal['GET', 'POST']

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)

# TODO: use a TypeVar
FuncType = Callable[..., Any]
CoroType = Callable[..., Coroutine[Any, Any, Any]]
