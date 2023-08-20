from __future__ import annotations

from ._compat import get_origin


def is_list_type(typ: type) -> bool:
    return (get_origin(typ) or typ) == list
