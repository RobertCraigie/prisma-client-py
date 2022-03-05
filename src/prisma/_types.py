from typing import Callable, Coroutine, TypeVar, Type, Tuple, Any
from pydantic import BaseModel
from typing_extensions import (
    TypedDict as TypedDict,
    Protocol as Protocol,
    Literal as Literal,
    get_args as get_args,
    runtime_checkable as runtime_checkable,
)

Method = Literal['GET', 'POST']

CallableT = TypeVar('CallableT', bound='FuncType')
BaseModelT = TypeVar('BaseModelT', bound=BaseModel)

# TODO: use a TypeVar everywhere
FuncType = Callable[..., Any]
CoroType = Callable[..., Coroutine[Any, Any, Any]]


@runtime_checkable
class InheritsGeneric(Protocol):
    __orig_bases__: Tuple['_GenericAlias']


class _GenericAlias(Protocol):
    __origin__: Type[object]
