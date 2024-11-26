from __future__ import annotations

import json
from typing import Any
from decimal import Decimal
from datetime import datetime
from typing_extensions import TypeGuard

from .types import JsonOutputTaggedValue
from ...fields import Base64


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


def deserialize_tagged_value(tagged: JsonOutputTaggedValue) -> Any:
    if tagged['$type'] == 'BigInt':
        return int(tagged['value'])
    elif tagged['$type'] == 'Bytes':
        return Base64.fromb64(tagged['value'])
    elif tagged['$type'] == 'DateTime':
        return datetime.fromisoformat(tagged['value'])
    elif tagged['$type'] == 'Decimal':
        return Decimal(tagged['value'])
    elif tagged['$type'] == 'Json':
        return json.loads(tagged['value'])
