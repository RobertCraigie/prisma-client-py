from typing import Callable, Coroutine, TypeVar, Type, Tuple, Any, Union
from pydantic import BaseModel
from typing_extensions import (
    TypeGuard as TypeGuard,
    TypedDict as TypedDict,
    Protocol as Protocol,
    Literal as Literal,
    get_args as get_args,
    runtime_checkable as runtime_checkable,
)

Method = Literal['GET', 'POST']

_T = TypeVar('_T')

CallableT = TypeVar('CallableT', bound='FuncType')
BaseModelT = TypeVar('BaseModelT', bound=BaseModel)

# TODO: use a TypeVar everywhere
FuncType = Callable[..., object]
CoroType = Callable[..., Coroutine[Any, Any, object]]


@runtime_checkable
class InheritsGeneric(Protocol):
    __orig_bases__: Tuple['_GenericAlias']


class _GenericAlias(Protocol):
    __origin__: Type[object]


class NotGiven:
    """Represents cases where a value has not been explicitly given.


    Useful when `None` is not a possible default value.
    """

    def __repr__(self) -> str:
        return 'NOT_GIVEN'


NOT_GIVEN = NotGiven()
NotGivenOr = Union[_T, NotGiven]

PrismaMethod = Literal[
    # raw queries
    'query_raw',
    'query_first',
    'execute_raw',
    # mutatitive queries
    'create',
    'delete',
    'update',
    'upsert',
    'create_many',
    'delete_many',
    'update_many',
    # read queries
    'count',
    'group_by',
    'find_many',
    'find_first',
    'find_first_or_raise',
    'find_unique',
    'find_unique_or_raise',
]
