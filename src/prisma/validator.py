import sys
import contextlib
from types import ModuleType
from contextvars import ContextVar
from functools import lru_cache, wraps
from typing import Optional, Type, TypeVar, Iterator, Any, cast

from pydantic import BaseModel, Extra, create_model_from_typeddict
from pydantic.decorator import validate_arguments
from pydantic.typing import is_typeddict
from jinja2.debug import tb_set_next

from ._types import Protocol, CallableT, runtime_checkable


__all__ = (
    'validate',
    'disable_validation',
)

# NOTE: we should use bound=TypedDict but mypy does not support this
T = TypeVar('T')
_validation_enabled: ContextVar[bool] = ContextVar('_validation_enabled', default=True)


class Config:
    extra: Extra = Extra.forbid


@runtime_checkable
class CachedModel(Protocol):
    __pydantic_model__: BaseModel


class FunctionValidator(Protocol):
    def validate(self, *args: Any, **kwargs: Any) -> BaseModel:
        ...


def _get_module(typ: Type[Any]) -> ModuleType:
    return sys.modules[typ.__module__]


@lru_cache(maxsize=None)
def _patch_pydantic() -> None:
    """Pydantic does not resolve forward references for TypedDict types properly yet

    see https://github.com/samuelcolvin/pydantic/pull/2761
    """
    from pydantic import annotated_types

    create_model = annotated_types.create_model_from_typeddict

    # cache the created models so that recursive references can be resolved correctly.
    # should be noted that pydantic caches models differently, using a __pydantic_model__
    # attribute on the type, however this does not work for our use case as this cache
    # would disregard Config changes
    @lru_cache(maxsize=None)
    def patched_create_model(
        typeddict_cls: Type[Any], **kwargs: Any
    ) -> Type[BaseModel]:
        kwargs.setdefault('__module__', typeddict_cls.__module__)
        return create_model(typeddict_cls, **kwargs)

    annotated_types.create_model_from_typeddict = patched_create_model


_patch_pydantic()


def validate(type: Type[T], data: Any) -> T:  # pylint: disable=redefined-builtin
    """Validate untrusted data matches a given TypedDict

    For example:

    from prisma import validate, types

    def user_create_handler(data: Any) -> None:
        validated = validate(types.UserCreateInput, data)
        user = await client.user.create(data=validated)
    """
    if not is_typeddict(type):
        raise TypeError(f'Only TypedDict types are supported, got: {type} instead.')

    # we cannot use pydantic's builtin type -> model resolver
    # as we need to be able to update forward references
    if isinstance(type, CachedModel):
        # cache the model on the type object, mirroring how pydantic works
        # mypy thinks this is unreachable, we know it isn't, just ignore
        model = type.__pydantic_model__  # type: ignore[unreachable]
    else:
        # pyright is more strict than mypy here, we also don't care about the
        # incorrectly inferred type as we have verified that the given type
        # is indeed a TypedDict
        model = create_model_from_typeddict(
            type, __config__=Config  # pyright: reportGeneralTypeIssues=false
        )
        model.update_forward_refs(**vars(_get_module(type)))
        type.__pydantic_model__ = model  # type: ignore

    instance = model.parse_obj(data)
    return cast(T, instance.dict(exclude_unset=True))


@contextlib.contextmanager
def disable_validation() -> Iterator[None]:
    """Disable runtime validation of query arguments"""
    enabled = _validation_enabled.get()

    try:
        _validation_enabled.set(False)
        yield
    finally:
        _validation_enabled.set(enabled)


def lazy_validate_arguments(func: CallableT) -> CallableT:
    """Wrapper over pydantic's `@validate_arguments` decorator with some modifications.

    - internal BaseModel is only built when needed
    - validation can be disabled with `disable_validation()`
    """

    validator: Optional[FunctionValidator] = None

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal validator

        if not _validation_enabled.get():
            return func(*args, **kwargs)

        if validator is None:
            validator = cast(FunctionValidator, validate_arguments(func))

        # validate the arguments using pydantic and call the function ourselves so that
        # we can remove some noise from the error traceback if a validation error ocurrs
        try:
            validator.validate(*args, **kwargs)
        finally:
            # remove some redundant traceback frames from pydantic
            _maybe_rewrite_tb()

        return func(*args, **kwargs)

    return cast(CallableT, wrapper)


def _maybe_rewrite_tb() -> None:
    """Remove all of the traceback frames after the current frame"""
    _, _, tb = sys.exc_info()
    if tb is not None:
        tb_set_next(tb, None)
