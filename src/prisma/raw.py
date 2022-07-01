from array import array
import binascii
from datetime import datetime
from ._types import BaseModelT

from typing import Any, Dict, Optional, Type, Union, List

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

"""
export function deserializeRawResults(rows: Array<Record<string, TypedValue>>): unknown[] {
  return rows.map((row) => {
    const mappedRow = {} as Record<string, unknown>
    for (const key of Object.keys(row)) {
      mappedRow[key] = deserializeValue(row[key])
    }
    return mappedRow
  })
}
"""


def parse_raw_list(
    raw_list: list[Any], model: Optional[Type[BaseModelT]] = None
) -> Union[List[BaseModelT], Any]:
    return [parse_raw_obj(obj, model) for obj in raw_list]


def parse_raw_obj(
    raw_obj: Dict[Any, Any], model: Optional[Type[BaseModelT]] = None
) -> Union[List[BaseModelT], Any]:
    print(raw_obj)
    obj = {}
    for attr in raw_obj:
        print(raw_obj[attr])
        obj[attr] = parse_raw_value(raw_obj[attr])
    if model is not None:
        return model.parse_obj(obj)
    return obj


def parse_raw_value(raw_value: Dict[Any, Any]):
    _type = raw_value['prisma__type']
    value = raw_value['prisma__value']

    if _type in _casts:
        return _casts[_type](value)
    else:
        return value


def _cast_datetime(value: str):
    return datetime.fromisoformat(value)


def _cast_bigint(value: str):
    return int(value)


def _cast_bytes(value: str):
    return binascii.a2b_base64(value)


def _cast_decimal(value: str):
    return float(value)


def _cast_time(value: str):
    # return new Date(`1970-01-01T${value}Z`)
    return datetime.fromisoformat(f'1970-01-01T${value}Z')


def _cast_array(value: list[Any]) -> Union[list[Any], Any]:
    return map(parse_raw_value, value)


_casts = {
    'bigint': _cast_bigint,
    'bytes': _cast_bytes,
    'decimal': _cast_decimal,
    'datetime': _cast_datetime,
    'date': _cast_datetime,
    'time': _cast_time,
    'array': _cast_array,
}
