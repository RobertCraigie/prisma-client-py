import sys
import enum
import importlib
from pathlib import Path
from keyword import iskeyword
from importlib import machinery, util as importlib_util
from importlib.abc import InspectLoader
from contextvars import ContextVar
from typing import (
    Any,
    Optional,
    List,
    Tuple,
    Union,
    Iterator,
    Dict,
    Type,
    TYPE_CHECKING,
)

import click
from pydantic import (
    BaseModel as PydanticBaseModel,
    BaseSettings,
    Extra,
    Field as FieldInfo,
    validator,
    root_validator,
)

try:
    from pydantic.env_settings import SettingsSourceCallable
except ImportError:
    SettingsSourceCallable = Any  # type: ignore


# NOTE: this does not represent all the data that is passed by prisma

ATOMIC_FIELD_TYPES = ['Int', 'BigInt', 'Float']

TYPE_MAPPING = {
    'String': 'str',
    'DateTime': 'datetime.datetime',
    'Boolean': 'bool',
    'Int': 'int',
    'Float': 'float',
    'BigInt': 'int',
    'Json': '\'fields.Json\'',
}
FILTER_TYPES = [
    'String',
    'DateTime',
    'Boolean',
    'Int',
    'BigInt',
    'Float',
    'Json',
]

data_ctx: ContextVar['Data'] = ContextVar('data_ctx')


def get_config() -> 'Config':
    return data_ctx.get().generator.config


def get_datamodel() -> 'Datamodel':
    return data_ctx.get().dmmf.datamodel


def _module_spec_serializer(spec: machinery.ModuleSpec) -> str:
    assert spec.origin is not None, 'Cannot serialize module with no origin'
    return spec.origin


class BaseModel(PydanticBaseModel):
    class Config:
        json_encoders: Dict[Type[Any], Any] = {
            machinery.ModuleSpec: _module_spec_serializer,
        }


class InterfaceChoices(str, enum.Enum):
    sync = 'sync'
    asyncio = 'asyncio'


class Module(BaseModel):
    spec: machinery.ModuleSpec

    class Config(BaseModel.Config):
        arbitrary_types_allowed: bool = True

    @validator('spec', pre=True, allow_reuse=True)
    @classmethod
    def spec_validator(cls, value: Optional[str]) -> machinery.ModuleSpec:
        spec: Optional[machinery.ModuleSpec] = None

        if value is None:
            value = 'prisma/partial_types.py'

        path = Path.cwd().joinpath(value)
        if path.exists():
            spec = importlib_util.spec_from_file_location(
                'prisma.partial_type_generator', value
            )
        elif value.startswith('.'):
            raise ValueError(
                f'No file found at {value} and relative imports are not allowed.'
            )
        else:
            try:
                spec = importlib_util.find_spec(value)
            except ModuleNotFoundError:
                spec = None

        if spec is None:
            raise ValueError(f'Could not find a python file or module at {value}')

        return spec

    def run(self) -> None:
        importlib.invalidate_caches()
        mod = importlib_util.module_from_spec(self.spec)
        loader = self.spec.loader
        assert loader is not None, 'Expected an import loader to exist.'
        assert isinstance(
            loader, InspectLoader
        ), f'Cannot execute module from loader type: {type(loader)}'

        try:
            loader.exec_module(mod)
        except:
            print('An exception ocurred while running the partial type generator')
            raise


class Data(BaseModel):
    """Root model for the data that prisma provides to the generator."""

    datamodel: str
    version: str
    generator: 'Generator'
    dmmf: 'DMMF' = FieldInfo(alias='dmmf')
    schema_path: str = FieldInfo(alias='schemaPath')
    datasources: List['Datasource'] = FieldInfo(alias='datasources')

    # TODO
    other_generators: List[Any] = FieldInfo(alias='otherGenerators')

    @classmethod
    def parse_obj(cls, obj: Any) -> 'Data':
        data = super().parse_obj(obj)
        data_ctx.set(data)
        return data


class Datasource(BaseModel):
    # TODO: provider enums
    name: str
    provider: str
    active_provider: str = FieldInfo(alias='activeProvider')
    url: 'OptionalValueFromEnvVar'


class Generator(BaseModel):
    name: str
    output: 'ValueFromEnvVar'
    provider: 'ValueFromEnvVar'
    config: 'Config'
    binary_targets: List['ValueFromEnvVar'] = FieldInfo(alias='binaryTargets')
    preview_features: List[str] = FieldInfo(alias='previewFeatures')

    @validator('binary_targets')
    @classmethod
    def warn_binary_targets(
        cls, targets: List['ValueFromEnvVar']
    ) -> List['ValueFromEnvVar']:
        if targets and any(target.value != 'native' for target in targets):
            click.echo(
                click.style(
                    'Warning: '
                    'The binaryTargets option is not currently supported by Prisma Client Python',
                    fg='yellow',
                ),
                file=sys.stdout,
            )

        return targets


class ValueFromEnvVar(BaseModel):
    value: str
    from_env_var: Optional[str] = FieldInfo(alias='fromEnvVar')


class OptionalValueFromEnvVar(BaseModel):
    value: Optional[str]
    from_env_var: Optional[str] = FieldInfo(alias='fromEnvVar')


class Config(BaseSettings):
    """Custom generator config options."""

    interface: InterfaceChoices = InterfaceChoices.asyncio
    partial_type_generator: Optional[Module]
    recursive_type_depth: int = FieldInfo(default=5)

    class Config(BaseSettings.Config):
        extra: Extra = Extra.forbid
        use_enum_values: bool = True
        env_prefix: str = 'prisma_py_config_'
        allow_population_by_field_name: bool = True

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            # prioritise env settings over init settings
            return env_settings, init_settings, file_secret_settings

    @root_validator(pre=True)
    @classmethod
    def removed_http_option_validator(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        http = values.get('http')
        if http is not None:
            if http in {'aiohttp', 'httpx-async'}:
                option = 'asyncio'
            elif http in {'requests', 'httpx-sync'}:
                option = 'sync'
            else:  # pragma: no cover
                # invalid http option, let pydantic handle the error
                return values

            raise ValueError(
                'The http option has been removed in favour of the interface option.\n'
                '  Please remove the http option from your Prisma schema and replace it with:\n'
                f'  interface = "{option}"'
            )
        return values

    @validator('partial_type_generator', pre=True, always=True, allow_reuse=True)
    @classmethod
    def partial_type_generator_converter(cls, value: Optional[str]) -> Optional[Module]:
        try:
            return Module(spec=value)
        except ValueError:
            if value is None:
                # no config value passed and the default location was not found
                return None
            raise

    @validator('recursive_type_depth', always=True, allow_reuse=True)
    @classmethod
    def recursive_type_depth_validator(cls, value: int) -> int:
        if value < -1 or value in {0, 1}:
            raise ValueError('Value must equal -1 or be greater than 1.')
        return value


class DMMF(BaseModel):
    datamodel: 'Datamodel'

    # TODO
    prisma_schema: Any = FieldInfo(alias='schema')


class Datamodel(BaseModel):
    enums: List['Enum']
    models: List['Model']


class Enum(BaseModel):
    name: str
    db_name: Optional[str] = FieldInfo(alias='dbName')
    values: List['EnumValue']


class EnumValue(BaseModel):
    name: str
    db_name: Optional[str] = FieldInfo(alias='dbName')


class Model(BaseModel):
    name: str
    is_embedded: bool = FieldInfo(alias='isEmbedded')
    db_name: Optional[str] = FieldInfo(alias='dbName')
    is_generated: bool = FieldInfo(alias='isGenerated')

    if TYPE_CHECKING:
        # pylint thinks all_fields is not an iterable
        all_fields: List['Field']
    else:
        all_fields: List['Field'] = FieldInfo(alias='fields')

    @property
    def related_models(self) -> Iterator['Model']:
        models = get_datamodel().models
        for field in self.relational_fields:
            for model in models:
                if field.type == model.name:
                    yield model

    @property
    def relational_fields(self) -> Iterator['Field']:
        for field in self.all_fields:
            if field.is_relational:
                yield field

    @property
    def scalar_fields(self) -> Iterator['Field']:
        for field in self.all_fields:
            if not field.is_relational:
                yield field

    @property
    def atomic_fields(self) -> Iterator['Field']:
        for field in self.all_fields:
            if field.type in ATOMIC_FIELD_TYPES:
                yield field

    @property
    def has_relational_fields(self) -> bool:
        try:
            next(self.relational_fields)
        except StopIteration:
            return False
        else:
            return True


class Field(BaseModel):
    name: str

    # TODO: switch to enums
    kind: str
    type: str

    is_id: bool = FieldInfo(alias='isId')
    is_list: bool = FieldInfo(alias='isList')
    is_unique: bool = FieldInfo(alias='isUnique')
    is_required: bool = FieldInfo(alias='isRequired')
    is_read_only: bool = FieldInfo(alias='isReadOnly')
    is_generated: bool = FieldInfo(alias='isGenerated')
    is_updated_at: bool = FieldInfo(alias='isUpdatedAt')

    default: Optional[Union['DefaultValue', str]]
    has_default_value: bool = FieldInfo(alias='hasDefaultValue')

    relation_name: Optional[str] = FieldInfo(alias='relationName')
    relation_on_delete: Optional[str] = FieldInfo(alias='relationOnDelete')
    relation_to_fields: Optional[List[str]] = FieldInfo(alias='relationToFields')
    relation_from_fields: Optional[List[str]] = FieldInfo(alias='relationFromFields')

    @root_validator
    @classmethod
    def scalar_type_validator(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        kind = values.get('kind')
        type_ = values.get('type')

        if kind == 'scalar':
            if type_ is not None and type_ not in TYPE_MAPPING:
                raise ValueError(f'Unsupported scalar field type: {type_}')

        return values

    @validator('name')
    @classmethod
    def name_validator(cls, name: str) -> str:
        if getattr(BaseModel, name, None):
            raise ValueError(
                f'Field name "{name}" shadows a BaseModel attribute; '
                f'use a different field name with \'@map("{name}")\'.'
            )

        if iskeyword(name):
            raise ValueError(
                f'Field name "{name}" shadows a Python keyword; '
                f'use a different field name with \'@map("{name}")\'.'
            )

        return name

    # TODO: cache the properties
    @property
    def python_type(self) -> str:
        type_ = self._actual_python_type
        if self.is_list:
            return f'List[{type_}]'
        return type_

    @property
    def python_type_as_string(self) -> str:
        type_ = self._actual_python_type
        if self.is_list:
            type_ = type_.replace('\'', '\\\'')
            return f'\'List[{type_}]\''

        if not type_.startswith('\''):
            type_ = f'\'{type_}\''

        return type_

    @property
    def _actual_python_type(self) -> str:
        if self.kind == 'enum':
            return f'\'enums.{self.type}\''

        if self.kind == 'object':
            return f'\'models.{self.type}\''

        try:
            return TYPE_MAPPING[self.type]
        except KeyError as exc:
            # TODO: handle this better
            raise RuntimeError(
                f'Could not parse {self.name} due to unknown type: {self.type}',
            ) from exc

    @property
    def create_input_type(self) -> str:
        if self.kind != 'object':
            return self.python_type

        if self.is_list:
            return f'\'{self.type}CreateManyNestedWithoutRelationsInput\''

        return f'\'{self.type}CreateNestedWithoutRelationsInput\''

    @property
    def where_input_type(self) -> str:
        typ = self.type
        if typ in FILTER_TYPES:
            return f'Union[{self._actual_python_type}, \'types.{typ}Filter\']'
        if self.is_relational:
            if self.is_list:
                return f'\'{typ}ListRelationFilter\''
            return f'\'{typ}RelationFilter\''
        return self.python_type

    @property
    def relational_args_type(self) -> str:
        if self.is_list:
            return f'FindMany{self.type}Args'
        return f'{self.type}Args'

    @property
    def required_on_create(self) -> bool:
        return (
            self.is_required
            and not self.is_updated_at
            and not self.has_default_value
            and not self.relation_name
        )

    @property
    def is_optional(self) -> bool:
        return not (self.is_required and not self.relation_name)

    @property
    def is_relational(self) -> bool:
        return self.relation_name is not None

    @property
    def is_atomic(self) -> bool:
        return self.type in ATOMIC_FIELD_TYPES

    def maybe_optional(self, typ: str) -> str:
        """Wrap the given type string within `Optional` if applicable"""
        if self.is_required or self.is_relational:
            return typ
        return f'Optional[{typ}]'

    def get_update_input_type(self) -> str:
        if self.is_atomic:
            if self.is_list:
                raise NotImplementedError(
                    'Atomic updates for scalar list types not implemented yet.'
                )
            return f'Union[Atomic{self.type}Input, {self.python_type}]'

        if self.kind == 'object':
            if self.is_list:
                return f'\'{self.type}UpdateManyWithoutRelationsInput\''
            return f'\'{self.type}UpdateOneWithoutRelationsInput\''

        return self.python_type

    def get_relational_model(self) -> Optional['Model']:
        if not self.is_relational:
            return None

        name = self.type
        for model in get_datamodel().models:
            if model.name == name:
                return model
        return None


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
Datasource.update_forward_refs()
