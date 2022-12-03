from __future__ import annotations

import binascii
from datetime import datetime
from ._types import BaseModelT

from typing import Any, Callable, Dict, Optional, Type, Union, List

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


def deserialize_raw_results(
    raw_list: list[Any], model: Optional[Type[BaseModelT]] = None
) -> Union[List[BaseModelT], Any]:
    return [deserialize_value(obj, model) for obj in raw_list]


def deserialize_value(
    raw_obj: Dict[Any, Any], model: Optional[Type[BaseModelT]] = None
) -> Union[List[BaseModelT], Any]:
    print(raw_obj)
    obj = {}
    for attr in raw_obj:
        raw_value = raw_obj[attr]
        print(raw_value)
        _type = raw_value['prisma__type']
        value = raw_value['prisma__value']
        obj[attr] = (
            _deserializers[_type](value) if _type in _deserializers else value
        )
    if model is not None:
        return model.parse_obj(obj)
    return obj


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


_deserializers: Dict[str, Callable[..., Any]] = {
    'bigint': _deserialize_bigint,
    'bytes': _deserialize_bytes,
    'decimal': _deserialize_decimal,
    'datetime': _deserialize_datetime,
    'date': _deserialize_datetime,
    'time': _deserialize_time,
    'array': _deserialize_array,
}
