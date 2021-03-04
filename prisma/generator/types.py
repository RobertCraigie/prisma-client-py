from typing import Dict
from .._types import TypedDict


__all__ = (
    'PartialModelField',
    'PartialModelFields',
)


class PartialModelField(TypedDict):
    name: str
    alias: str
    optional: bool
    type: str


PartialModelFields = Dict[str, PartialModelField]
