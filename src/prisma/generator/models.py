import sys
import enum
import importlib
from pathlib import Path
from keyword import iskeyword
from itertools import chain
from importlib import machinery, util as importlib_util
from importlib.abc import InspectLoader
from contextvars import ContextVar
from typing import (
    Any,
    Iterable,
    NoReturn,
    Optional,
    List,
    Tuple,
    Union,
    Iterator,
    Dict,
    Type,
    TYPE_CHECKING,
    cast,
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
from pydantic.fields import PrivateAttr

try:
    from pydantic.env_settings import SettingsSourceCallable
except ImportError:
    SettingsSourceCallable = Any  # type: ignore


from .utils import Faker, Sampler, clean_multiline
from ..utils import DEBUG_GENERATOR
from .._constants import QUERY_BUILDER_ALIASES
from ..errors import UnsupportedListTypeError
from ..binaries.constants import ENGINE_VERSION


# NOTE: this does not represent all the data that is passed by prisma

ATOMIC_FIELD_TYPES = ['Int', 'BigInt', 'Float']

TYPE_MAPPING = {
    'String': 'str',
    'Bytes': '\'fields.Base64\'',
    'DateTime': 'datetime.datetime',
    'Boolean': 'bool',
    'Int': 'int',
    'Float': 'float',
    'BigInt': 'int',
    'Json': '\'fields.Json\'',
}
FILTER_TYPES = [
    'String',
    'Bytes',
    'DateTime',
    'Boolean',
    'Int',
    'BigInt',
    'Float',
    'Json',
]

FAKER: Faker = Faker()

data_ctx: ContextVar['Data'] = ContextVar('data_ctx')


def get_config() -> 'Config':
    return data_ctx.get().generator.config


def get_datamodel() -> 'Datamodel':
    return data_ctx.get().dmmf.datamodel


def get_list_types() -> Iterable[Tuple[str, str]]:
    # WARNING: do not edit this function without also editing Field.is_supported_scalar_list_type()
    return chain(
        ((t, TYPE_MAPPING[t]) for t in FILTER_TYPES),
        ((enum.name, f'\'enums.{enum.name}\'') for enum in get_datamodel().enums),
    )


def sql_param(num: int = 1) -> str:
    # TODO: add case for sqlserver
    active_provider = data_ctx.get().datasources[0].active_provider
    if active_provider == 'postgresql':
        return f'${num}'

    # TODO: test
    if active_provider == 'mongodb':  # pragma: no cover
        raise RuntimeError('no-op')

    # SQLite and MySQL use this style so just default to it
    return '?'


def raise_err(msg: str) -> NoReturn:
    raise TemplateError(msg)


def _module_spec_serializer(spec: machinery.ModuleSpec) -> str:
    assert spec.origin is not None, 'Cannot serialize module with no origin'
    return spec.origin


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed: bool = True
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
    """Root model for the data that prisma provides to the generator.

    WARNING: only one instance of this class may exist at any given time and
    instances should only be constructed using the Data.parse_obj() method
    """

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

    def to_params(self) -> Dict[str, Any]:
        """Get the parameters that should be sent to Jinja templates"""
        params = vars(self)
        params['type_schema'] = Schema.from_data(self)

        # add utility functions
        for func in [get_list_types, sql_param, clean_multiline, raise_err]:
            params[func.__name__] = func

        return params

    @root_validator(pre=True, allow_reuse=True)
    @classmethod
    def validate_version(cls, values: Dict[Any, Any]) -> Dict[Any, Any]:
        # TODO: test this
        version = values.get('version')
        if not DEBUG_GENERATOR and version != ENGINE_VERSION:
            raise ValueError(
                f'Prisma Client Python expected Prisma version: {ENGINE_VERSION} '
                f'but got: {version}\n'
                '  If this is intentional, set the PRISMA_PY_DEBUG_GENERATOR environment '
                'variable to 1 and try again.\n'
                '  Are you sure you are generating the client using the python CLI?\n'
                '  e.g. python3 -m prisma generate'
            )
        return values


class Datasource(BaseModel):
    # TODO: provider enums
    name: str
    provider: str
    active_provider: str = FieldInfo(alias='activeProvider')
    url: 'OptionalValueFromEnvVar'


class Generator(BaseModel):
    name: str
    output: 'ValueFromEnvVar'
    provider: 'OptionalValueFromEnvVar'
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
    compound_primary_key: Optional['PrimaryKey'] = FieldInfo(alias='primaryKey')
    unique_indexes: List['UniqueIndex'] = FieldInfo(alias='uniqueIndexes')
    _sampler: Sampler = PrivateAttr()

    if TYPE_CHECKING:
        # pylint thinks all_fields is not an iterable
        all_fields: List['Field']
    else:
        all_fields: List['Field'] = FieldInfo(alias='fields')

    # no idea why mypy throws this error
    def __init__(self, **data: Any) -> None:  # type: ignore[no-redef]
        super().__init__(**data)
        self._sampler = Sampler(self)

    @root_validator(allow_reuse=True)
    @classmethod
    def validate_compound_constraints_are_unique(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        # protect against https://github.com/prisma/prisma/issues/10456
        fields = cast(List['Field'], values.get('all_fields', []))
        pkey = cast(Optional[PrimaryKey], values.get('compound_primary_key'))
        if pkey is not None:
            for field in fields:
                if field.name == pkey.name:
                    raise CompoundConstraintError(constraint=pkey)

        indexes = cast(List[UniqueIndex], values.get('unique_indexes'))
        for field in fields:
            for constraint in indexes:
                if field.name == constraint.name:
                    raise CompoundConstraintError(constraint=constraint)

        return values

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

    # TODO: support combined unique constraints
    @property
    def id_field(self) -> Optional['Field']:
        """Find a field that can be passed to the model's `WhereUnique` filter"""
        for field in self.scalar_fields:  # pragma: no branch
            if field.is_id or field.is_unique:
                return field
        return None

    @property
    def has_relational_fields(self) -> bool:
        try:
            next(self.relational_fields)
        except StopIteration:
            return False
        else:
            return True

    @property
    def plural_name(self) -> str:
        name = self.name
        if name.endswith('s'):
            return name
        return f'{name}s'

    def resolve_field(self, name: str) -> 'Field':
        for field in self.all_fields:
            if field.name == name:
                return field

        raise LookupError(f'Could not find a field with name: {name}')

    def sampler(self) -> Sampler:
        return self._sampler

    def get_fields_of_type(self, typ: str) -> Iterator['Field']:
        for field in self.scalar_fields:
            if field.type == typ:
                yield field


class Constraint(BaseModel):
    name: str
    fields: List[str]

    @root_validator(pre=True, allow_reuse=True)
    @classmethod
    def resolve_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        name = values.get('name')
        if isinstance(name, str):
            return values

        values['name'] = '_'.join(values['fields'])
        return values


class PrimaryKey(Constraint):
    pass


class UniqueIndex(Constraint):
    pass


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

    _last_sampled: Optional[str] = PrivateAttr()

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

        if name == 'prisma':
            raise ValueError(
                'Field name "prisma" shadows a Prisma Client Python method; '
                'use a different field name with \'@map("prisma")\'.'
            )

        if name in QUERY_BUILDER_ALIASES:
            raise ValueError(
                f'Field name "{name}" shadows an internal keyword; '
                f'use a different field name with \'@map("{name}")\''
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
        if self.is_relational:
            if self.is_list:
                return f'\'{typ}ListRelationFilter\''
            return f'\'{typ}RelationFilter\''

        if self.is_list:
            self.check_supported_scalar_list_type()
            return f'\'types.{typ}ListFilter\''

        if typ in FILTER_TYPES:
            return f'Union[{self._actual_python_type}, \'types.{typ}Filter\']'

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
            and not self.is_list
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
        if self.kind == 'object':
            if self.is_list:
                return f'\'{self.type}UpdateManyWithoutRelationsInput\''
            return f'\'{self.type}UpdateOneWithoutRelationsInput\''

        if self.is_list:
            self.check_supported_scalar_list_type()
            return f'\'types.{self.type}ListUpdate\''

        if self.is_atomic:
            return f'Union[Atomic{self.type}Input, {self.python_type}]'

        return self.python_type

    def check_supported_scalar_list_type(self) -> None:
        if not self.type in FILTER_TYPES and self.kind != 'enum':
            raise UnsupportedListTypeError(self.type)

    def get_relational_model(self) -> Optional['Model']:
        if not self.is_relational:
            return None

        name = self.type
        for model in get_datamodel().models:
            if model.name == name:
                return model
        return None

    def get_corresponding_enum(self) -> Optional['Enum']:
        typ = self.type
        for enum in get_datamodel().enums:
            if enum.name == typ:
                return enum
        return None  # pragma: no cover

    def get_sample_data(self, *, increment: bool = True) -> str:
        # returning the same data that was last sampled is useful
        # for documenting methods like upsert() where data is duplicated
        if not increment and self._last_sampled is not None:
            return self._last_sampled

        sampled = self._get_sample_data()
        if self.is_list:
            sampled = f'[{sampled}]'

        self._last_sampled = sampled
        return sampled

    def _get_sample_data(self) -> str:
        # pylint: disable=no-else-return,too-many-return-statements
        if self.is_relational:  # pragma: no cover
            raise RuntimeError('Data sampling for relational fields not supported yet')

        if self.kind == 'enum':
            enum = self.get_corresponding_enum()
            assert enum is not None, self.type
            return f'enums.{enum.name}.{FAKER.from_list(enum.values).name}'

        typ = self.type
        if typ == 'Boolean':
            return str(FAKER.boolean())
        elif typ == 'Int':
            return str(FAKER.integer())
        elif typ == 'String':
            return f'\'{FAKER.string()}\''
        elif typ == 'Float':
            return f'{FAKER.integer()}.{FAKER.integer() // 10000}'
        elif typ == 'BigInt':  # pragma: no cover
            return str(FAKER.integer() * 12)
        elif typ == 'DateTime':
            # TODO: random dates
            return 'datetime.datetime.utcnow()'
        elif typ == 'Json':
            return f'Json({{\'{FAKER.string()}\': True}})'
        elif typ == 'Bytes':
            return f'Base64.encode(b\'{FAKER.string()}\')'
        else:  # pragma: no cover
            raise RuntimeError(f'Sample data not supported for {typ} yet')


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


from .schema import Schema
from .errors import CompoundConstraintError, TemplateError
