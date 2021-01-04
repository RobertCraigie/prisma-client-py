import enum
from contextvars import ContextVar
from typing import Any, Optional, List, Union
from pydantic import BaseModel, Extra, Field as BaseField

from .utils import pascalize, camelize, decamelize


# NOTE: this does not represent all the data that is passed by prisma

config_ctx: ContextVar['Config'] = ContextVar('config_ctx')


class TransformChoices(str, enum.Enum):
    none = 'none'
    snake_case = 'snake_case'
    camel_case = 'camelCase'
    pascal_case = 'PascalCase'


class Data(BaseModel):
    """Root model for the data that prisma provides to the generator."""

    datamodel: str
    version: str
    generator: 'Generator'
    dmmf: 'DMMF' = BaseField(alias='dmmf')
    schema_path: str = BaseField(alias='schemaPath')

    # TODO
    data_sources: Any = BaseField(alias='dataSources')
    other_generators: List[Any] = BaseField(alias='otherGenerators')

    @classmethod
    def parse_obj(cls, obj: Any) -> 'Data':
        data = super().parse_obj(obj)
        config_ctx.set(data.generator.config)
        return data


class Generator(BaseModel):
    name: str
    output: str
    provider: str
    config: 'Config'
    binary_targets: List[str] = BaseField(alias='binaryTargets')
    preview_features: List[str] = BaseField(alias='previewFeatures')


class Config(BaseModel):
    """Custom generator config options."""

    transform_fields: Optional[TransformChoices] = BaseField(alias='transformFields')

    class Config:
        extra = Extra.forbid
        use_enum_values = True
        allow_population_by_field_name = True


class DMMF(BaseModel):
    datamodel: 'Datamodel'

    # TODO
    prisma_schema: Any = BaseField(alias='schema')


class Datamodel(BaseModel):
    enums: List['Enum']
    models: List['Model']


class Enum(BaseModel):
    name: str
    db_name: Optional[str] = BaseField(alias='dbName')
    values: List['EnumValue']


class EnumValue(BaseModel):
    name: str
    db_name: Optional[str] = BaseField(alias='dbName')


class Model(BaseModel):
    name: str
    is_embedded: bool = BaseField(alias='isEmbedded')
    db_name: Optional[str] = BaseField(alias='dbName')
    is_generated: bool = BaseField(alias='isGenerated')
    all_fields: List['Field'] = BaseField(alias='fields')


# TODO: Json probably isn't right
TYPE_MAPPING = {
    'String': 'str',
    'DateTime': 'datetime.datetime',
    'Boolean': 'bool',
    'Int': 'int',
    'Float': 'float',
    'Json': 'dict',
}


class Field(BaseModel):
    name: str

    # TODO: switch to enums
    kind: str
    type: str

    is_id: bool = BaseField(alias='isId')
    is_list: bool = BaseField(alias='isList')
    is_unique: bool = BaseField(alias='isUnique')
    is_required: bool = BaseField(alias='isRequired')
    is_read_only: bool = BaseField(alias='isReadOnly')
    is_generated: bool = BaseField(alias='isGenerated')
    is_updated_at: bool = BaseField(alias='isUpdatedAt')

    default: Optional[Union['DefaultValue', str]]
    has_default_value: bool = BaseField(alias='hasDefaultValue')

    relation_name: Optional[str] = BaseField(alias='relationName')
    relation_on_delete: Optional[str] = BaseField(alias='relationOnDelete')
    relation_to_fields: Optional[List[str]] = BaseField(alias='relationToFields')
    relation_from_fields: Optional[List[str]] = BaseField(alias='relationFromFields')

    # TODO: cache the properties
    @property
    def python_type(self) -> str:
        if self.kind == 'enum':
            return f'{self.type}Enum'

        if self.kind == 'object':
            return f'\'{self.type}\''

        try:
            return TYPE_MAPPING[self.type]
        except KeyError as exc:
            # TODO: handle this better
            raise RuntimeError(
                f'Could not parse {self.name} due to unknown type: {self.type}',
            ) from exc

    @property
    def python_case(self) -> str:
        transform = config_ctx.get().transform_fields
        if transform == TransformChoices.camel_case:
            return camelize(self.name)

        if transform == TransformChoices.pascal_case:
            return pascalize(self.name)

        if transform == TransformChoices.none:
            return self.name

        return decamelize(self.name)

    @property
    def required_on_create(self) -> bool:
        return (
            self.is_required and not self.is_updated_at and not self.has_default_value
        )


class DefaultValue(BaseModel):
    args: Any
    name: str


Enum.update_forward_refs()
DMMF.update_forward_refs()
Data.update_forward_refs()
Field.update_forward_refs()
Model.update_forward_refs()
Datamodel.update_forward_refs()
Generator.update_forward_refs()
