from __future__ import annotations

import json
import inspect
import logging
import warnings
from functools import singledispatch
from typing import Any, Dict, Mapping
from typing_extensions import TypedDict, Required

from ...utils import DEBUG
from ..._constants import QUERY_BUILDER_ALIASES
from ..._helpers import is_mapping
from ..._types import PrismaMethod, NotGiven

# Note: this is a codegen'd module
from ...bases import _PrismaModel


log: logging.Logger = logging.getLogger(__name__)


class SingleQuery(TypedDict, total=False):
    action: Required[str]
    query: Required[FieldQuery]
    modelName: str


class FieldQuery(TypedDict, total=False):
    arguments: dict[str, ArgumentValue]
    selection: SelectionSet


# TODO: more detailed types
SelectionSet = Dict[str, Any]
ArgumentValue = object


class QueryInput(TypedDict, total=False):
    method: Required[PrismaMethod]
    arguments: Required[dict[str, object]]
    model: type[_PrismaModel] | None


METHOD_TO_ACTION: dict[PrismaMethod, str] = {
    'create': 'createOne',
    'delete': 'deleteOne',
    'update': 'updateOne',
    'upsert': 'upsertOne',
    'query_raw': 'queryRaw',
    'create_many': 'createMany',
    'execute_raw': 'executeRaw',
    'delete_many': 'deleteMany',
    'update_many': 'updateMany',
    'count': 'aggregate',
    'group_by': 'groupBy',
    'find_many': 'findMany',
    'find_first': 'findFirst',
    'find_first_or_raise': 'findFirstOrThrow',
    'find_unique': 'findUnique',
    'find_unique_or_raise': 'findUniqueOrThrow',
}


def _method_to_action(method: PrismaMethod) -> str:
    action = METHOD_TO_ACTION.get(method)
    if action is None:
        raise RuntimeError('TODO')
    return action


def serialize_single_query(
    *,
    method: PrismaMethod,
    arguments: dict[str, object],
    model: type['_PrismaModel'] | None = None,
    extend_selection: dict[str, object] | None = None,
) -> str:
    query = build_single_query(
        method=method,
        arguments=arguments,
        model=model,
        extend_selection=extend_selection,
    )
    return dumps(query, indent=2 if DEBUG else None)


def serialize_batched_query(*, queries: list[QueryInput]) -> str:
    batched = [build_single_query(**query) for query in queries]
    return dumps(
        {
            'batch': batched,
            'transaction': {},
        },
        indent=2 if DEBUG else None,
    )


def build_single_query(
    *,
    method: PrismaMethod,
    arguments: dict[str, object],
    model: type['_PrismaModel'] | None = None,
    extend_selection: dict[str, object] | None = None,
) -> SingleQuery:
    request: SingleQuery = {
        'action': _method_to_action(method),
        'query': _build_query(
            _transform_aliases(arguments), extend_selection=extend_selection
        ),
    }

    if model is not None:
        # TODO: better error message if unset
        request['modelName'] = model.__prisma_model__

    return request


def _build_query(
    args: Mapping[str, object],
    *,
    extend_selection: dict[str, object] | None = None,
) -> FieldQuery:
    data = _strip_not_given_args(args)
    include = data.pop('include', None)

    return {
        'arguments': data,
        'selection': _build_selection(
            include=include, extend_selection=extend_selection
        ),
    }


def _build_selection(
    *,
    include: object | None,
    extend_selection: dict[str, object] | None,
) -> SelectionSet:
    selection: SelectionSet = {
        '$scalars': True,
        '$composites': True,
        **(extend_selection or {}),
    }

    if is_mapping(include):
        for key, value in include.items():
            if value is True:
                selection[key] = True
            elif is_mapping(value):
                selection[key] = _build_query(value)

    return selection


ITERABLES: tuple[type[Any], ...] = (list, tuple, set)


def _transform_aliases(arguments: dict[str, Any]) -> dict[str, Any]:
    """Transform dict keys to match global aliases

    e.g. order_by -> orderBy
    """
    # TODO: this should use type information to transform instead of just naively matching keys
    transformed = dict()
    for key, value in arguments.items():
        alias = QUERY_BUILDER_ALIASES.get(key, key)
        if isinstance(value, dict):
            transformed[alias] = _transform_aliases(arguments=value)
        elif isinstance(value, ITERABLES):
            # it is safe to map any iterable type to a list here as it is only being used
            # to serialise the query and we only officially support lists anyway
            transformed[alias] = [
                _transform_aliases(data) if isinstance(data, dict) else data  # type: ignore
                for data in value
            ]
        else:
            transformed[alias] = value
    return transformed


def _strip_not_given_args(args: Mapping[str, object]) -> dict[str, object]:
    result = {}
    for key, value in args.items():
        if value is None:
            warnings.warn(
                f'Encountered `None` value for `{key}`. Please use `prisma.NOT_GIVEN` instead.',
                DeprecationWarning,
                stacklevel=3,
            )
        elif isinstance(value, NotGiven):
            continue
        else:
            result[key] = value

    return result


@singledispatch
def serializer(obj: object) -> str:
    """Single dispatch generic function for serializing objects to JSON"""
    if inspect.isclass(obj):
        typ = obj
    else:
        typ = type(obj)

    raise TypeError(f'Type {typ} not serializable')


def dumps(obj: object, **kwargs: object) -> str:
    kwargs.setdefault('default', serializer)
    kwargs.setdefault('ensure_ascii', False)
    return json.dumps(obj, **kwargs)
