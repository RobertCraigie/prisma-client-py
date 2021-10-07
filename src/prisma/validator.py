import sys
from types import ModuleType
from functools import lru_cache
from typing import Type, TypeVar, Any, cast

from pydantic import BaseModel, Extra, create_model_from_typeddict
from pydantic.typing import is_typeddict

from ._types import Protocol, runtime_checkable


__all__ = ('validate',)

# NOTE: we should use bound=TypedDict but mypy does not support this
T = TypeVar('T')


class Config:
    extra: Extra = Extra.forbid


@runtime_checkable
class CachedModel(Protocol):
    __pydantic_model__: BaseModel


def _get_module(typ: Type[Any]) -> ModuleType:
    return sys.modules[typ.__module__]


@lru_cache(maxsize=None)
def patch_pydantic() -> None:
    """Pydantic does not resolve forward references for TypedDict types properly yet

    see https://github.com/samuelcolvin/pydantic/pull/2761
    """
    from pydantic import annotated_types

    create_model = annotated_types.create_model_from_typeddict

    def patched_create_model(
        typeddict_cls: Type[Any], **kwargs: Any
    ) -> Type[BaseModel]:
        kwargs.setdefault('__module__', typeddict_cls.__module__)
        return create_model(typeddict_cls, **kwargs)

    annotated_types.create_model_from_typeddict = patched_create_model


def validate(type: Type[T], data: Any) -> T:  # pylint: disable=redefined-builtin
    """Validate untrusted data matches a given TypedDict

    For example:

    from prisma import validate, types

    def user_create_handler(data: Any) -> None:
        validated = validate(types.UserCreateInput, data)
        user = await client.user.create(data=validated)
    """
    # avoid patching pydantic until we know we need to in case our
    # monkey patching fails
    patch_pydantic()

    if not is_typeddict(type):
        raise TypeError(f'Only TypedDict types are supported, got: {type} instead.')

    # we cannot use pydantic's builtin type -> model resolver
    # as we need to be able to update forward references
    if isinstance(type, CachedModel):
        # cache the model on the type object, mirroring how pydantic works
        # mypy thinks this is unreachable, we know it isn't, just ignore
        model = type.__pydantic_model__  # type: ignore[unreachable]
    else:
        # type ignore required as pydantic is typed with a custom
        # TypedDict type instead of the standard library version
        model = create_model_from_typeddict(type, __config__=Config)  # type: ignore
        model.update_forward_refs(**vars(_get_module(type)))
        type.__pydantic_model__ = model  # type: ignore

    instance = model.parse_obj(data)
    return cast(T, instance.dict(exclude_unset=True))
