from __future__ import annotations

import binascii
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


# From: https://github.com/prisma/prisma/blob/main/packages/client/src/runtime/utils/deserializeRawResults.ts
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
        return [deserialize_value(obj, model=model) for obj in raw_list]

    return [deserialize_value(obj) for obj in raw_list]


@overload
def deserialize_value(raw_obj: dict[str, Any]) -> dict[str, Any]:
    ...


@overload
def deserialize_value(
    raw_obj: Dict[str, object],
    model: Type[BaseModelT],
) -> BaseModelT:
    ...


def deserialize_value(
    raw_obj: Dict[Any, Any],
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
            _deserializers[prisma_type](value)
            if prisma_type in _deserializers
            else value
        )

    if model is not None:
        return model.parse_obj(new_obj)

    return new_obj


def _deserialize_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _deserialize_bigint(value: str) -> int:
    return int(value)


def _deserialize_bytes(value: str) -> bytes:
    return binascii.a2b_base64(value)


def _deserialize_decimal(value: str) -> float:
    return float(value)


def _deserialize_time(value: str) -> datetime:
    return datetime.fromisoformat(f'1970-01-01T${value}Z')


def _deserialize_array(value: list[Any]) -> Union[list[Any], Any]:
    return map(deserialize_value, value)


DESERIALIZERS: Dict[str, Callable[..., object]] = {
    'bigint': _deserialize_bigint,
    'bytes': _deserialize_bytes,
    'decimal': _deserialize_decimal,
    'datetime': _deserialize_datetime,
    'date': _deserialize_datetime,
    'time': _deserialize_time,
    'array': _deserialize_array,
}
