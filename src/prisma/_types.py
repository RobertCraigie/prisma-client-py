from __future__ import annotations

from typing import Any, Type, Tuple, Mapping, TypeVar, Callable, Coroutine
from typing_extensions import (
    Literal as Literal,
    NewType,
    Protocol as Protocol,
    TypedDict as TypedDict,
    TypeGuard as TypeGuard,
    get_args as get_args,
    runtime_checkable as runtime_checkable,
)

import httpx
from pydantic import BaseModel

Method = Literal['GET', 'POST']

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


# NOTE: we don't support some options as their type hints are not publicly exposed
# https://github.com/encode/httpx/discussions/1977
class HttpConfig(TypedDict, total=False):
    app: Callable[[Mapping[str, Any], Any], Any]
    http1: bool
    http2: bool
    limits: httpx.Limits
    timeout: None | float | httpx.Timeout
    trust_env: bool
    max_redirects: int


SortMode = Literal['default', 'insensitive']
SortOrder = Literal['asc', 'desc']

MetricsFormat = Literal['json', 'prometheus']


class _DatasourceOverrideOptional(TypedDict, total=False):
    env: str
    name: str


class DatasourceOverride(_DatasourceOverrideOptional):
    url: str


class _DatasourceOptional(TypedDict, total=False):
    env: str
    source_file_path: str | None


class Datasource(_DatasourceOptional):
    name: str
    url: str


TransactionId = NewType('TransactionId', str)
