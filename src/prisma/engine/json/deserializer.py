from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, TypeGuard, assert_never

from ...fields import Base64
from .types import JsonOutputTaggedValue


def deserialize(result: Any) -> Any:
    if not result:
        return result

    if isinstance(result, list):
        return list(map(deserialize, result))

    if isinstance(result, dict):
        if is_tagged_value(result):
            return result['value']  # XXX: will pydantic cast this?

        return {k: deserialize(v) for k, v in result.items()}

    return result


def is_tagged_value(value: dict[Any, Any]) -> TypeGuard[JsonOutputTaggedValue]:
    return isinstance(value.get('$type'), str)


def deserialize_tagged_value(tagged: JsonOutputTaggedValue) -> Any:  # JsOutputValue
    match tagged['$type']:
        case 'BigInt':
            return int(tagged['value'])
        case 'Bytes':
            return Base64.fromb64(tagged['value'])
        case 'DateTime':
            return datetime.fromisoformat(tagged['value'])
        case 'Decimal':
            return Decimal(tagged['value'])
        case 'Json':
            return json.loads(tagged['value'])

    return assert_never(tagged['$type'])
