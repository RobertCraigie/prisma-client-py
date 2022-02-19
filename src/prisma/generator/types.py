from typing import Dict
from .._types import TypedDict


__all__ = (
    'PartialModel',
    'PartialModelField',
)


class PartialModelField(TypedDict):
    name: str
    is_list: bool
    optional: bool
    type: str


class PartialModel(TypedDict):
    name: str
    from_model: str
    fields: Dict[str, PartialModelField]
