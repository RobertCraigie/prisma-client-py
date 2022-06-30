# from pydantic import BaseModel
from datetime import datetime
from ._types import BaseModelT

from typing import Any, Dict, Optional, Type, Union, List


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
    # return value
    if _type in _casts:
        return _casts[_type](value)


def _cast_any(value: Any):
    return value


def _cast_datetime(value: Any):
    if isinstance(value, str):
        return datetime.fromisoformat(str(value))
    return value


def _cast_bigint(value: Any):
    if isinstance(value, str):
        return int(value)
    return value


_casts = {
    'null': _cast_any,
    'bool': _cast_any,
    'string': _cast_any,
    'int': _cast_any,
    'datetime': _cast_datetime,
    'bigint': _cast_bigint,
}
