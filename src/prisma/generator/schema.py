from enum import Enum
from typing import Any, Dict, List, Union

from pydantic import BaseModel
from pydantic.class_validators import root_validator

from .models import Data, Model as ModelInfo, PrimaryKey


class Kind(str, Enum):
    alias = 'alias'
    union = 'union'
    typeddict = 'typeddict'


class PrismaType(BaseModel):
    name: str
    kind: Kind
    subtypes: List['PrismaType'] = []

    @classmethod
    def from_subtypes(
        cls, subtypes: List['PrismaType'], **kwargs: Any
    ) -> Union['PrismaUnion', 'PrismaAlias']:
        """Return either a `PrismaUnion` or a `PrismaAlias` depending on the number of subtypes"""
        if len(subtypes) > 1:
            return PrismaUnion(subtypes=subtypes, **kwargs)

        return PrismaAlias(subtypes=subtypes, **kwargs)


class PrismaDict(PrismaType):
    kind: Kind = Kind.typeddict
    fields: Dict[str, str]
    total: bool


class PrismaUnion(PrismaType):
    kind: Kind = Kind.union
    subtypes: List[PrismaType]


class PrismaAlias(PrismaType):
    kind: Kind = Kind.alias
    to: str

    @root_validator(pre=True)
    @classmethod
    def transform_to(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if 'to' not in values and 'subtypes' in values:
            values['to'] = values['subtypes'][0].name
        return values


class Schema(BaseModel):
    models: List['Model']

    @classmethod
    def from_data(cls, data: Data) -> 'Schema':
        models = [Model(info=model) for model in data.dmmf.datamodel.models]
        return cls(models=models)

    def get_model(self, name: str) -> 'Model':
        for model in self.models:
            if model.info.name == name:
                return model

        raise LookupError(f'Unknown model: {name}')


class Model(BaseModel):
    info: ModelInfo

    @property
    def where_unique(self) -> PrismaType:
        info = self.info
        model = info.name
        subtypes: List[PrismaType] = [
            PrismaDict(
                total=True,
                name=f'_{model}WhereUnique_{field.name}_Input',
                fields={
                    field.name: field.python_type,
                },
            )
            for field in info.scalar_fields
            if field.is_id or field.is_unique
        ]

        for key in [info.compound_primary_key, *info.unique_indexes]:
            if key is None:
                continue

            if isinstance(key, PrimaryKey):
                name = f'_{model}CompoundPrimaryKey'
            else:
                name = f'_{model}Compound{key.name}Key'

            subtypes.append(
                PrismaDict(
                    name=name,
                    total=True,
                    fields={
                        key.name: f'{name}Inner',
                    },
                    subtypes=[
                        PrismaDict(
                            total=True,
                            name=f'{name}Inner',
                            fields={
                                field.name: field.python_type
                                for field in map(info.resolve_field, key.fields)
                            },
                        )
                    ],
                )
            )

        return PrismaType.from_subtypes(subtypes, name=f'{model}WhereUniqueInput')


Schema.update_forward_refs()
PrismaType.update_forward_refs()
PrismaDict.update_forward_refs()
PrismaAlias.update_forward_refs()
