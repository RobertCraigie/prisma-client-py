from __future__ import annotations

from typing import Mapping
from typing_extensions import TypeGuard


def is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def is_mapping(value: object) -> TypeGuard[Mapping[str, object]]:
    return isinstance(value, Mapping)
