from typing import Awaitable, Callable, Dict, Optional, Type
from typing_extensions import NewType

from pydantic import BaseModel

from .._types import PrismaMethod


class MiddlewareParams(BaseModel):
    # TODO: test mutating this
    method: PrismaMethod
    """The Prisma Client Python method that was queried..

    For example, for the `prisma.users.find_unique()` method, this will be set to `find_unique`.
    """

    model: Optional[Type[BaseModel]]
    """The Pydantic model that will be used to parse the results"""

    arguments: Dict[str, object]
    """Arguments that were passed to this query."""


MiddlewareResult = NewType('MiddlewareResult', object)

# TODO: sync types too
NextMiddleware = Callable[[MiddlewareParams], Awaitable[MiddlewareResult]]
MiddlewareFunc = Callable[
    [MiddlewareParams, NextMiddleware],
    Awaitable[MiddlewareResult],
]
