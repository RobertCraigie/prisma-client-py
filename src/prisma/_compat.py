from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, Callable, TypeVar
from asyncio import get_running_loop as get_running_loop

import pydantic
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from ._types import CallableT
from .utils import make_optional


_ModelT = TypeVar('_ModelT', bound=BaseModel)


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
PYDANTIC_V2 = pydantic.VERSION.startswith('2.')

if TYPE_CHECKING:
    # TODO: just copy these in
    from pydantic.typing import (
        is_typeddict as is_typeddict,
        get_args as get_args,
    )

    BaseSettings = BaseModel
    BaseSettingsConfig = pydantic.BaseConfig  # type: ignore

    class GenericModel(BaseModel):
        ...

else:
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

    if PYDANTIC_V2:
        from pydantic import ValidationInfo, model_validator

        class BaseSettings(BaseModel):
            @model_validator(mode='before')
            def root_validator(cls, values: Any, info: ValidationInfo) -> Any:
                return _env_var_resolver(cls, values)

    else:
        from pydantic import BaseSettings


# refactored config
if TYPE_CHECKING:
    from pydantic import ConfigDict as ConfigDict
else:
    if PYDANTIC_V2:
        from pydantic import ConfigDict
    else:
        ConfigDict = None


ENV_VAR_KEY = '$env'

def _env_var_resolver(
    model_cls: type[BaseModel], values: Any
) -> dict[str, Any]:
    assert isinstance(values, dict)

    for key, field_info in model_cls.model_fields.items():
        extra = _resolve_json_schema_extra(field_info)
        env_var = extra.get(ENV_VAR_KEY)
        if not env_var:
            continue

        assert isinstance(env_var, str)
        if key in values:
            continue

        value = os.environ.get(env_var)
        if value is not None:
            values[key] = value

    return values


def _resolve_json_schema_extra(field: FieldInfo) -> dict[str, Any]:
    extra = field.json_schema_extra
    if callable(extra):
        raise RuntimeError('Unexpected field json schema is a function')

    return extra or {}


def model_json(model: BaseModel, indent: int | None = None) -> str:
    if PYDANTIC_V2:
        return model.model_dump_json(indent=indent)

    return model.json(indent=indent)  # type: ignore


def model_dict(
    model: BaseModel,
    exclude_unset: bool = False,
) -> dict[str, Any]:
    if PYDANTIC_V2:
        return model.model_dump(exclude_unset=exclude_unset)

    return model.dict(exclude_unset=exclude_unset)  # type: ignore


def model_rebuild(model: type[BaseModel]) -> None:
    if PYDANTIC_V2:
        model.model_rebuild()
    else:
        model.update_forward_refs()  # type: ignore


def model_parse(model: type[_ModelT], obj: Any) -> _ModelT:
    if PYDANTIC_V2:
        return model.model_validate(obj)
    else:
        return model.parse_obj(obj)  # type: ignore


def Field(*, env: str | None = None, **extra: Any) -> Any:
    if PYDANTIC_V2:
        # we store environment variable metadata in $env
        # as a workaround to support BaseSettings behaviour ourselves
        # as we can't depend on pydantic-settings
        json_schema_extra = None
        if env:
            json_schema_extra = {ENV_VAR_KEY: env}

        return pydantic.Field(**extra, json_schema_extra=json_schema_extra)

    return pydantic.Field(**extra, env=env)  # type: ignore


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
