from typing import Awaitable, Callable, Dict, Optional
from typing_extensions import Literal, NewType

from pydantic import BaseModel


class MiddlewareParams(BaseModel):
    # TODO: support mutating this
    method: str
    """The Prisma Client Python method that was queried..

    For example, for the `prisma.users.find_unique()` method, this will be set to `find_unique`.

    **warning**: mutating this property will not do anything, if you need to change the resulting method please use `.prisma_method` instead.
    """

    # TODO: remove this once above support is implemented
    prisma_method: str
    """The underlying Prisma method corresponding to this query.

    For example, for the `prisma.users.update_many()` method, this will be set to `updateMany`.
    """

    operation: Literal['query', 'mutation']
    """The internal GraphQL operation"""

    model_name: Optional[str]
    """The name of the Prisma model. May be `None` for non-type-safe raw queries."""

    arguments: Dict[str, object]
    """Arguments that were passed to this query."""


MiddlewareResult = NewType('MiddlewareResult', object)

NextMiddleware = Callable[[MiddlewareParams], Awaitable[MiddlewareResult]]

MiddlewareFunc = Callable[
    [MiddlewareParams, NextMiddleware],
    Awaitable[MiddlewareResult],
]
