from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Callable, cast
from asyncio import get_running_loop as get_running_loop

import pydantic
from pydantic import BaseConfig, BaseModel

from ._types import CallableT
from .utils import make_optional


if TYPE_CHECKING:
    # in pyright >= 1.190 classmethod is a generic type, this causes errors when
    # verifying type completeness as pydantic validators are typed to return a
    # classmethod without any generic parameters.
    # we fix these errors by overriding the typing of these validator functions
    # to simply return the callable back unchanged.

    def root_validator(
        *,
        pre: bool = False,
        allow_reuse: bool = False,
        skip_on_failure: bool = False,
    ) -> Callable[[CallableT], CallableT]:
        ...

    def validator(
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


# Pydantic v2 compat
pydantic_major_version = int(pydantic.VERSION.split('.')[0])

if TYPE_CHECKING:
    from pydantic import BaseSettings as BaseSettings

    # TODO: just copy these in
    from pydantic.typing import (
        is_typeddict as is_typeddict,
        get_args as get_args,
    )

    BaseSettingsConfig = BaseSettings.Config

    class GenericModel(BaseModel):
        ...

else:
    try:
        from pydantic_settings import BaseSettings
    except ImportError:
        try:
            from pydantic.v1 import BaseSettings
        except ImportError:
            # TODO: helpful error here in v2
            from pydantic import BaseSettings

    try:
        BaseSettingsConfig = BaseSettings.Config
    except AttributeError:
        BaseSettingsConfig = BaseConfig

    try:
        from pydantic.v1.typing import is_typeddict, get_args
    except ImportError:
        from pydantic.typing import is_typeddict, get_args

    try:
        from pydantic.generics import GenericModel as PydanticGenericModel

        class GenericModel(PydanticGenericModel, BaseModel):
            ...

    except ImportError:
        # note: there no longer needs to be a distinction between these in v2
        from pydantic import BaseModel as GenericModel


def model_json(model: BaseModel, indent: int) -> str:
    if pydantic_major_version == 1:
        return model.json(indent=indent)

    return model.model_dump_json(indent=indent)  # type: ignore


def Field(*, env: str | None = None, **extra: Any) -> Any:
    if pydantic_major_version == 1:
        return pydantic.Field(**extra, env=env)  # type: ignore
    return pydantic.Field(**extra, validation_alias=env)


if pydantic_major_version == 1:
    pydantic_extra_ignore = pydantic.Extra.ignore
else:
    pydantic_extra_ignore = cast(Any, 'ignore')

if sys.version_info[:2] < (3, 8):
    # cached_property doesn't define type hints so just ignore it
    # it is functionally equivalent to the standard property anyway
    if TYPE_CHECKING:
        cached_property = property
    else:
        from cached_property import cached_property as cached_property
else:
    from functools import cached_property as cached_property


if TYPE_CHECKING:
    import nodejs as _nodejs

    nodejs = make_optional(_nodejs)
else:
    try:
        import nodejs
    except ImportError:
        nodejs = None


def removeprefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string
