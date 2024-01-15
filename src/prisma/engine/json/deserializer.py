from __future__ import annotations

from typing import Mapping
from typing_extensions import TypeGuard

from .types import OutputTaggedValue
from ..._helpers import is_list, is_mapping


def deserialize(value: object) -> object:
    if not value:
        return value

    if is_list(value):
        return [deserialize(entry) for entry in value]

    if is_mapping(value):
        if is_tagged_value(value):
            return deserialize_tagged_value(value)

        return {key: deserialize(item) for key, item in value.items()}

    return value


def is_tagged_value(
    value: Mapping[str, object]
) -> TypeGuard[OutputTaggedValue]:
    return isinstance(value.get('$type'), str)


def deserialize_tagged_value(tagged: OutputTaggedValue) -> object:
    if tagged['$type'] == 'FieldRef':
        raise RuntimeError('Cannot deserialize FieldRef values yet')

    return tagged['value']
