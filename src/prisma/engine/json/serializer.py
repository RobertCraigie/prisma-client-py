from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Type, TypedDict, cast
from decimal import Decimal
from inspect import isclass
from datetime import datetime, timezone
from functools import singledispatch
from contextvars import ContextVar

from pydantic import BaseModel

from .types import (
    JsonQuery,
    DateTaggedValue,
    JsonQueryAction,
    JsonTaggedValue,
    BytesTaggedValue,
    JsonSelectionSet,
    DecimalTaggedValue,
    JsonFieldSelection,
    JsonInputTaggedValue,
)
from ..._types import PrismaMethod
from ...errors import InvalidModelError, UnknownModelError, UnknownRelationalFieldError
from ...fields import Json, Base64
from ..._compat import model_fields
from ..._builder import _is_prisma_model_type, _prisma_model_for_field
from ..._constants import QUERY_BUILDER_ALIASES

if TYPE_CHECKING:
    from ...bases import _PrismaModel  # noqa: TID251
    from ...types import Serializable  # noqa: TID251


METHOD_TO_ACTION: dict[PrismaMethod, JsonQueryAction] = {
    # raw queries
    'query_raw': 'queryRaw',
    'execute_raw': 'executeRaw',
    # mutatitive queries
    'create': 'createOne',
    'delete': 'deleteOne',
    'update': 'updateOne',
    'upsert': 'upsertOne',
    'create_many': 'createMany',
    'delete_many': 'deleteMany',
    'update_many': 'updateMany',
    # read queries
    'count': 'aggregate',
    'group_by': 'groupBy',
    'find_many': 'findMany',
    'find_first': 'findFirst',
    'find_first_or_raise': 'findFirstOrThrow',
    'find_unique': 'findUnique',
    'find_unique_or_raise': 'findUniqueOrThrow',
}


class _SerializeContext(TypedDict):
    method: PrismaMethod
    arguments: dict[str, Any]
    prisma_models: set[str]
    relational_field_mappings: dict[str, dict[str, str]]
    model: type[BaseModel] | None
    root_selection: JsonSelectionSet | None


_serialize_context: ContextVar[_SerializeContext] = ContextVar('_serialize_context')


def serialize(
    *,
    method: PrismaMethod,
    arguments: dict[str, Any],
    prisma_models: set[str],
    relational_field_mappings: dict[str, dict[str, str]],
    model: type[BaseModel] | None = None,
    root_selection: JsonSelectionSet | None = None,
) -> JsonQuery:
    token = _serialize_context.set(cast(_SerializeContext, locals()))
    try:
        query: JsonQuery = {
            'action': METHOD_TO_ACTION[method],
            'query': serialize_field_selection(transform_aliases(arguments)),
        }
    finally:
        _serialize_context.reset(token)

    if model is None or is_raw_action(method):
        return query

    if not (_is_prisma_model_type(model) and hasattr(model, '__prisma_model__')):
        raise InvalidModelError(model)

    query['modelName'] = model.__prisma_model__
    return query


def is_raw_action(method: PrismaMethod) -> bool:
    return method in {'execute_raw', 'query_raw'}


def transform_aliases(arguments: dict[str, Any]) -> dict[str, Any]:
    """Transform dict keys to match global aliases

    e.g. order_by -> orderBy
    """
    transformed = {}
    for key, value in arguments.items():
        alias = QUERY_BUILDER_ALIASES.get(key, key)
        if isinstance(value, dict):
            transformed[alias] = transform_aliases(arguments=value)
        elif isinstance(value, (list, tuple, set)):
            # it is safe to map any iterable type to a list here as it is only being used
            # to serialise the query and we only officially support lists anyway
            transformed[alias] = [
                transform_aliases(data) if isinstance(data, dict) else data  # type: ignore
                for data in value
            ]
        else:
            transformed[alias] = value
    return transformed


def serialize_field_selection(arguments: dict[str, Any]) -> JsonFieldSelection:
    context = _serialize_context.get()
    selection_set: JsonSelectionSet = {}

    if context['root_selection']:
        selection_set = context['root_selection'].copy()
    elif context['model'] and not is_raw_action(context['method']):
        selection_set = {'$scalars': True, '$composites': True}

    if include := arguments.pop('include', None):
        add_included_relations(selection_set, include)

    return {
        'arguments': {key: value for key, value in arguments.items() if value is not None},
        'selection': selection_set,
    }


def get_relational_model(current_model: type[_PrismaModel], field: str) -> type[_PrismaModel]:
    """Returns the model that the field is related to.

    Raises UnknownModelError if the current model is invalid.
    Raises UnknownRelationalFieldError if the field does not exist.
    """
    name = getattr(current_model, '__prisma_model__', ...)
    if name is ...:
        raise InvalidModelError(current_model)

    name = cast(str, name)

    context = _serialize_context.get()
    try:
        mappings = context['relational_field_mappings'][name]
    except KeyError as exc:
        raise UnknownModelError(name) from exc

    if field not in mappings:
        raise UnknownRelationalFieldError(model=current_model.__name__, field=field)

    try:
        info = model_fields(current_model)[field]
    except KeyError as exc:
        raise UnknownRelationalFieldError(model=current_model.__name__, field=field) from exc

    model = _prisma_model_for_field(info, name=field, parent=current_model)
    if not model:
        raise RuntimeError(
            f"The `{field}` field doesn't appear to be a Prisma Model type. "
            + 'Is the field a pydantic.BaseModel type and does it have a `__prisma_model__` class variable?'
        )

    return model


def add_included_relations(selection_set: JsonSelectionSet, include: dict[str, Any]):
    for key, value in include.items():
        if not value:
            continue

        context = _serialize_context.get()
        token = _serialize_context.set(
            {
                **context,
                'arguments': value,
                'model': get_relational_model(cast(Type['_PrismaModel'], context['model']), key),
                'root_selection': None,
            },
        )

        try:
            selection_set[key] = serialize_field_selection({} if value is True else value)
        finally:
            _serialize_context.reset(token)


@singledispatch
def serializer(obj: Any) -> Serializable | JsonInputTaggedValue:
    """Single dispatch generic function for serializing objects to JSON"""
    if isclass(obj):
        typ = obj
    else:
        typ = type(obj)

    raise TypeError(f'Type {typ} not serializable')


@serializer.register(datetime)
def serialize_datetime(dt: datetime) -> DateTaggedValue:
    """Format a datetime object to an ISO8601 string with a timezone.

    This assumes naive datetime objects are in UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        dt = dt.astimezone(timezone.utc)

    # truncate microseconds to 3 decimal places
    # https://github.com/RobertCraigie/prisma-client-py/issues/129
    dt = dt.replace(microsecond=int(dt.microsecond / 1000) * 1000)
    return {'$type': 'DateTime', 'value': dt.isoformat()}


@serializer.register(Json)
def serialize_json(obj: Json) -> JsonTaggedValue:
    """Serialize a Json wrapper to a json string.

    This is used as a hook to override our default behaviour when building
    queries which would treat data like {'hello': 'world'} as a Data node
    when we instead want it to be rendered as a raw json string.

    This should only be used for fields that are of the `Json` type.
    """
    return {'$type': 'Json', 'value': dumps(obj.data)}


@serializer.register(Base64)
def serialize_base64(obj: Base64) -> BytesTaggedValue:
    """Serialize a Base64 wrapper object to raw binary data"""
    return {'$type': 'Bytes', 'value': str(obj)}


@serializer.register(Decimal)
def serialize_decimal(obj: Decimal) -> DecimalTaggedValue:
    """Serialize a Decimal object to a string"""
    return {'$type': 'Decimal', 'value': str(obj)}


def dumps(obj: Any, **kwargs: Any) -> str:
    kwargs.setdefault('default', serializer)
    kwargs.setdefault('ensure_ascii', False)
    return json.dumps(obj, **kwargs)
