from typing import Dict, Optional
from .._types import TypedDict


__all__ = (
    'PartialModelField',
    'PartialModelFields',
)


class PartialModelField(TypedDict):
    name: str
    is_list: bool
    optional: bool
    type: str
    documentation: Optional[str]
    is_relational: bool


PartialModelFields = Dict[str, PartialModelField]
