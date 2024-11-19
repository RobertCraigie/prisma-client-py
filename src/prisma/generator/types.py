from abc import abstractmethod
from typing import Any, Dict, Mapping, Optional

from .._types import TypedDict

__all__ = (
    'PartialModel',
    'PartialModelField',
    'MetaFieldsInterface',
)


class PartialModelField(TypedDict):
    name: str
    is_list: bool
    optional: bool
    type: str
    documentation: Optional[str]
    is_relational: bool
    composite_type: Optional[object]


class PartialModel(TypedDict):
    name: str
    from_model: str
    fields: Mapping[str, PartialModelField]


class MetaFieldsInterface:
    @staticmethod
    @abstractmethod
    def get_meta_fields() -> Dict[Any, PartialModelField]:
        ...
