from __future__ import annotations

import json
from decimal import Decimal
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Type,
    Union,
    overload,
)

from ._types import BaseModelT
from .fields import Base64


# From: https://github.com/prisma/prisma/blob/main/packages/client/src/runtime/utils/deserializeRawResults.ts
# Last checked: 2022-12-04
"""
type PrismaType =
  | 'int'
  | 'bigint'
  | 'float'
  | 'double'
  | 'string'
  | 'enum'
  | 'bytes'
  | 'bool'
  | 'char'
  | 'decimal'
  | 'json'
  | 'xml'
  | 'uuid'
  | 'datetime'
  | 'date'
  | 'time'
  | 'array'
  | 'null'
"""


@overload
def deserialize_raw_results(
    raw_list: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    ...


@overload
def deserialize_raw_results(
    raw_list: list[dict[str, object]],
    model: Type[BaseModelT],
) -> list[BaseModelT]:
    ...


def deserialize_raw_results(
    raw_list: list[dict[str, Any]],
    model: Type[BaseModelT] | None = None,
) -> Union[list[BaseModelT], list[dict[str, Any]]]:
    """Deserialize a list of raw query results into their rich Python types.

    If `model` is given, convert each result into the corresponding model.
    Otherwise results are returned as a dictionary
    """
    if model is not None:
        return [
            deserialize_value(obj, model=model, for_model=True)
            for obj in raw_list
        ]

    return [deserialize_value(obj, for_model=False) for obj in raw_list]


# NOTE: this very weird `for_model` API is simply here as a workaround for
# https://github.com/RobertCraigie/prisma-client-py/issues/638
#
# This should hopefully be removed soon.


@overload
def deserialize_value(
    raw_obj: dict[str, Any],
    *,
    for_model: bool,
) -> dict[str, Any]:
    ...


@overload
def deserialize_value(
    raw_obj: Dict[str, object],
    *,
    for_model: bool,
    model: Type[BaseModelT],
) -> BaseModelT:
    ...


def deserialize_value(
    raw_obj: Dict[Any, Any],
    *,
    for_model: bool,
    model: Optional[Type[BaseModelT]] = None,
) -> Union[BaseModelT, Any]:
    # create a local reference to avoid performance penalty of global
    # lookups on some python versions
    _deserializers = DESERIALIZERS

    new_obj = {}
    for key, raw_value in raw_obj.items():
        value = raw_value['prisma__value']
        prisma_type = raw_value['prisma__type']

        new_obj[key] = (
            _deserializers[prisma_type](value, for_model)
            if prisma_type in _deserializers
            else value
        )

    if model is not None:
        return model.parse_obj(new_obj)

    return new_obj


def _deserialize_datetime(value: str, _for_model: bool) -> datetime:
    return datetime.fromisoformat(value)


def _deserialize_bigint(value: str, _for_model: bool) -> int:
    return int(value)


def _deserialize_bytes(value: str, _for_model: bool) -> Base64:
    return Base64.fromb64(value)


def _deserialize_decimal(value: str, _for_model: bool) -> Decimal:
    return Decimal(value)


def _deserialize_time(value: str, _for_model: bool) -> datetime:
    return datetime.fromisoformat(f'1970-01-01T${value}Z')


def _deserialize_array(
    value: list[Any], for_model: bool
) -> Union[list[Any], Any]:
    return [deserialize_value(entry, for_model=for_model) for entry in value]


def _deserialize_json(value: object, for_model: bool) -> object:
    # TODO: this may break if someone inserts just a string into the database
    if not isinstance(value, str) and for_model:
        # TODO: this is very bad
        #
        # Pydantic expects Json fields to be a `str`, we should implement
        # an actual workaround for this validation instead of wasting compute
        # on re-serializing the data.
        return json.dumps(value)

    # This may or may not have already been deserialized by the database
    return value


DESERIALIZERS: Dict[str, Callable[[Any, bool], object]] = {
    'bigint': _deserialize_bigint,
    'bytes': _deserialize_bytes,
    'decimal': _deserialize_decimal,
    'datetime': _deserialize_datetime,
    'date': _deserialize_datetime,
    'time': _deserialize_time,
    'array': _deserialize_array,
    'json': _deserialize_json,
}
