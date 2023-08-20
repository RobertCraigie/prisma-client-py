from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast
from asyncio import get_running_loop as get_running_loop

import pydantic
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .utils import make_optional


_T = TypeVar('_T')
_ModelT = TypeVar('_ModelT', bound=BaseModel)


# Pydantic v2 compat
PYDANTIC_V2 = pydantic.VERSION.startswith('2.')

# ---- validators ----


def field_validator(
    __field: str,
    *fields: str,
    pre: bool = False,
    check_fields: bool | None = None,
    always: bool | None = None,
    allow_reuse: bool | None = None,
) -> Callable[[_T], _T]:
    if PYDANTIC_V2:
        mode = 'before' if pre else 'after'
        return cast(
            Any,
            pydantic.field_validator(
                __field, *fields, mode=mode, check_fields=check_fields
            ),
        )

    kwargs = {}
    if always is not None:
        kwargs['always'] = always
    if allow_reuse is not None:
        kwargs['allow_reuse'] = allow_reuse

    return pydantic.validator(__field, *fields, **kwargs)  # type: ignore


def root_validator(
    *__args: Any,
    pre: bool = False,
    skip_on_failure: bool = False,
    allow_reuse: bool = False,
) -> Any:
    if PYDANTIC_V2:
        mode = 'before' if pre else 'after'
        return pydantic.model_validator(mode=mode)

    return cast(Any, pydantic.root_validator)(
        *__args,
        pre=pre,
        skip_on_failure=skip_on_failure,
        allow_reuse=allow_reuse,
    )


if TYPE_CHECKING:
    BaseSettings = BaseModel
    BaseSettingsConfig = pydantic.BaseConfig  # type: ignore

    BaseConfig = pydantic.BaseModel  # type: ignore

    from pydantic import GetCoreSchemaHandler as GetCoreSchemaHandler
    from pydantic_core import CoreSchema as CoreSchema, core_schema as core_schema

    class GenericModel(BaseModel):
        ...

else:
    if PYDANTIC_V2:
        from pydantic_core import CoreSchema, core_schema
        from pydantic import GetCoreSchemaHandler
    else:
        core_schema = None
        CoreSchema = None
        GetCoreSchemaHandler = None

    if PYDANTIC_V2:
        GenericModel = BaseModel
    else:
        from pydantic.generics import GenericModel as PydanticGenericModel

        class GenericModel(PydanticGenericModel, BaseModel):
            ...

    if PYDANTIC_V2:
        from pydantic import ValidationInfo, model_validator

        class BaseSettings(BaseModel):
            @model_validator(mode='before')
            def root_validator(cls, values: Any, info: ValidationInfo) -> Any:
                return _env_var_resolver(cls, values)

        BaseSettingsConfig = None

        BaseConfig = None

    else:
        from pydantic import BaseSettings

        BaseSettingsConfig = BaseSettings.Config

        BaseConfig = BaseModel.Config

# v1 re-exports
if TYPE_CHECKING:

    def get_args(t: type[Any]) -> tuple[Any, ...]:
        ...

    def is_union(tp: type[Any] | None) -> bool:
        ...

    def get_origin(t: type[Any]) -> type[Any] | None:
        ...

    def is_literal_type(type_: type[Any]) -> bool:
        ...

    def is_typeddict(type_: type[Any]) -> bool:
        ...

else:
    if PYDANTIC_V2:
        from pydantic.v1.typing import get_args as get_args
        from pydantic.v1.typing import is_union as is_union
        from pydantic.v1.typing import get_origin as get_origin
        from pydantic.v1.typing import is_typeddict as is_typeddict
        from pydantic.v1.typing import is_literal_type as is_literal_type
    else:
        from pydantic.typing import get_args as get_args
        from pydantic.typing import is_union as is_union
        from pydantic.typing import get_origin as get_origin
        from pydantic.typing import is_typeddict as is_typeddict
        from pydantic.typing import is_literal_type as is_literal_type


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
        env_var = _get_field_env_var(field_info)
        if not env_var:
            continue

        assert isinstance(env_var, str)
        if key in values:
            continue

        value = os.environ.get(env_var)
        if value is not None:
            values[key] = value

    return values


def _get_field_env_var(field: FieldInfo) -> str | None:
    if not PYDANTIC_V2:
        return field.field_info.extra.get('env')  # type: ignore

    extra = field.json_schema_extra
    if not extra:
        return None

    if callable(extra):
        raise RuntimeError('Unexpected field json schema is a function')

    return extra.get(ENV_VAR_KEY)


def model_fields(model: type[BaseModel]) -> dict[str, FieldInfo]:
    if PYDANTIC_V2:
        return model.model_fields
    return model.__fields__  # type: ignore


def model_field_type(field: FieldInfo) -> type | None:
    if PYDANTIC_V2:
        return field.annotation

    return field.type_  # type: ignore

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
