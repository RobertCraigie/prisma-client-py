import sys
from typing import TYPE_CHECKING, Callable
from asyncio import get_running_loop as get_running_loop

from ._types import CallableT


if TYPE_CHECKING:
    # in pyright >= 1.190 classmethod is a generic type, this causes errors when
    # verifying type completeness as pydantic validators are typed to return a
    # classmethod without any generic parameters.
    # we fix these errors by overriding the typing of these validator functions
    # to simply return the callable back unchanged.

    def root_validator(
        # pylint: disable=unused-argument
        *,
        pre: bool = False,
        allow_reuse: bool = False,
        skip_on_failure: bool = False,
    ) -> Callable[[CallableT], CallableT]:
        ...

    def validator(
        # pylint: disable=unused-argument
        *fields: str,
        pre: bool = ...,
        each_item: bool = ...,
        always: bool = ...,
        check_fields: bool = ...,
        whole: bool = ...,
        allow_reuse: bool = ...,
    ) -> Callable[[CallableT], CallableT]:
        ...


else:
    from pydantic import (
        validator as validator,
        root_validator as root_validator,
    )


if sys.version_info[:2] < (3, 8):
    # cached_property doesn't define type hints so just ignore it
    # it is functionally equivalent to the standard property anyway
    if TYPE_CHECKING:
        cached_property = property
    else:
        try:
            from cached_property import cached_property as cached_property
        except ImportError:  # pragma: no cover
            # If we can't import cached_property, fallback to the standard property
            cached_property = property
else:
    from functools import cached_property as cached_property
