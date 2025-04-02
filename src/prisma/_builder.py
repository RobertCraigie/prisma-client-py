from __future__ import annotations

import json
import decimal
import inspect
import logging
import datetime
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Union, Mapping, Iterable, ForwardRef, cast
from datetime import timezone
from textwrap import indent
from functools import singledispatch
from typing_extensions import Literal, TypeGuard, override

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from . import fields
from ._types import PrismaMethod
from .errors import InvalidModelError, UnknownModelError, UnknownRelationalFieldError
from ._compat import get_args, is_union, get_origin, model_fields, model_field_type
from ._typing import is_list_type
from .generator import PartialModelField, MetaFieldsInterface
from ._constants import QUERY_BUILDER_ALIASES

if TYPE_CHECKING:
    from .bases import _PrismaModel as PrismaModel  # noqa: TID251
    from .types import Serializable  # noqa: TID251


log: logging.Logger = logging.getLogger(__name__)

ChildType = Union['AbstractNode', str]

ITERABLES: tuple[type[Any], ...] = (list, tuple, set)

METHOD_OPERATION_MAPPING: dict[PrismaMethod, Operation] = {
    'create': 'mutation',
    'delete': 'mutation',
    'update': 'mutation',
    'upsert': 'mutation',
    'query_raw': 'mutation',
    'query_first': 'mutation',
    'create_many': 'mutation',
    'execute_raw': 'mutation',
    'delete_many': 'mutation',
    'update_many': 'mutation',
    'count': 'query',
    'group_by': 'query',
    'find_many': 'query',
    'find_first': 'query',
    'find_first_or_raise': 'query',
    'find_unique': 'query',
    'find_unique_or_raise': 'query',
}

METHOD_FORMAT_MAPPING: dict[PrismaMethod, str] = {
    'create': 'createOne{model}',
    'delete': 'deleteOne{model}',
    'update': 'updateOne{model}',
    'upsert': 'upsertOne{model}',
    'query_raw': 'queryRaw',
    'query_first': 'queryRaw',
    'create_many': 'createMany{model}',
    'execute_raw': 'executeRaw',
    'delete_many': 'deleteMany{model}',
    'update_many': 'updateMany{model}',
    'count': 'aggregate{model}',
    'group_by': 'groupBy{model}',
    'find_many': 'findMany{model}',
    'find_first': 'findFirst{model}',
    'find_first_or_raise': 'findFirst{model}OrThrow',
    'find_unique': 'findUnique{model}',
    'find_unique_or_raise': 'findUnique{model}OrThrow',
}

MISSING = object()
Operation = Literal['query', 'mutation']


class QueryBuilder:
    method: PrismaMethod
    """The name of the actions method that this query is for, e.g. `find_unique`"""

    method_format: str
    """Template denoting how the internal method name should be constructed, e.g. `findUnique{model}`"""

    operation: Operation
    """The GraphQL operatiom e.g. `query`, `mutation`"""

    model: type[PrismaModel] | None
    """The Pydantic model that will be used to parse the response.

    Used to extract the model name & build selections.
    """

    include: dict[str, Any] | None
    """Mapping of relational fields to include in the result"""

    arguments: dict[str, Any]
    """Arguments to pass to the query"""

    root_selection: list[str] | None
    """List of fields to select"""

    prisma_models: set[str]
    """The names of all models present in the schema.prisma"""

    relational_field_mappings: dict[str, dict[str, str]]
    """A mapping of model name to a mapping of field name to relational model name

    e.g. {'User': {'posts': 'Post'}}
    """

    __slots__ = (
        'method',
        'method_format',
        'operation',
        'model',
        'include',
        'arguments',
        'root_selection',
        'prisma_models',
        'relational_field_mappings',
    )

    def __init__(
        self,
        *,
        method: PrismaMethod,
        arguments: dict[str, Any],
        prisma_models: set[str],
        relational_field_mappings: dict[str, dict[str, str]],
        model: type[BaseModel] | None = None,
        root_selection: list[str] | None = None,
    ) -> None:
        self.method = method
        self.method_format = METHOD_FORMAT_MAPPING[method]
        self.operation = METHOD_OPERATION_MAPPING[method]
        self.root_selection = root_selection
        self.prisma_models = prisma_models
        self.relational_field_mappings = relational_field_mappings
        self.arguments = args = self._transform_aliases(arguments)
        self.include = args.pop('include', None)

        # Note: we ignore the `model` argument for raw queries as users may want to pass in a model
        # that isn't a `PrismaModel` because they've defined it manually & enforcing that
        # they subclass `PrismaModel` doesn't bring any real benefits.
        if model is None or method in {'execute_raw', 'query_raw', 'query_first'}:
            self.model = None
        else:
            if not _is_prisma_model_type(model) or not hasattr(model, '__prisma_model__'):
                raise InvalidModelError(model)

            self.model = model

    def build(self) -> str:
        """Build the payload that should be sent to the QueryEngine"""
        data: dict[str, object] = {
            'variables': {},
            'operation_name': self.operation,
            'query': self.build_query(),
        }
        return dumps(data)

    def build_query(self) -> str:
        """Build the GraphQL query

        Example query:

        query {
          result: findUniqueUser
          (
            where: {
              id: "ckq23ky3003510r8zll5m2hma"
            }
          )
          {
            id
            name
            profile {
              id
              user_id
              bio
            }
          }
        }
        """
        query = self._create_root_node().render()
        log.debug('Generated query: \n%s', query)
        return query

    def _create_root_node(self) -> 'RootNode':
        root = RootNode(builder=self)
        root.add(ResultNode.create(self))
        root.add(
            Selection.create(
                self,
                model=self.model,
                include=self.include,
                root_selection=self.root_selection,
            )
        )
        return root

    def get_default_fields(self, model: type[PrismaModel]) -> list[str]:
        """Returns a list of all the scalar fields of a model
        Raises UnknownModelError if the current model cannot be found.
        """
        name = getattr(model, '__prisma_model__', MISSING)
        if name is MISSING:
            raise InvalidModelError(model)

        name = model.__prisma_model__
        if name not in self.prisma_models:
            raise UnknownModelError(name)

        # by default we exclude every field that points to a PrismaModel as that indicates that it is a relational field
        # we explicitly keep fields that point to anything else, even other pydantic.BaseModel types, as they can be used to deserialize JSON
        return [
            field
            for field, info in model_fields(model).items()
            if not _field_is_prisma_model(info, name=field, parent=model)
        ]

    def get_relational_model(self, current_model: type[BaseModel], field: str) -> type[PrismaModel]:
        """Returns the model that the field is related to.

        Raises UnknownModelError if the current model is invalid.
        Raises UnknownRelationalFieldError if the field does not exist.
        """
        name = getattr(current_model, '__prisma_model__', MISSING)
        if name is MISSING:
            raise InvalidModelError(current_model)

        name = cast(str, name)

        try:
            mappings = self.relational_field_mappings[name]
        except KeyError as exc:
            raise UnknownModelError(name) from exc

        if field not in mappings:
            raise UnknownRelationalFieldError(model=current_model.__name__, field=field)

        try:
            info = model_fields(current_model)[field]
        except KeyError as exc:
            raise UnknownRelationalFieldError(model=current_model.__name__, field=field) from exc

        model = _prisma_model_for_field(info, name=field, parent=current_model)
        if not model:
            raise RuntimeError(
                f"The `{field}` field doesn't appear to be a Prisma Model type. "
                + 'Is the field a pydantic.BaseModel type and does it have a `__prisma_model__` class variable?'
            )

        return model

    def _transform_aliases(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Transform dict keys to match global aliases

        e.g. order_by -> orderBy
        """
        transformed = dict()
        for key, value in arguments.items():
            alias = QUERY_BUILDER_ALIASES.get(key, key)
            if isinstance(value, dict):
                transformed[alias] = self._transform_aliases(arguments=value)
            elif isinstance(value, ITERABLES):
                # it is safe to map any iterable type to a list here as it is only being used
                # to serialise the query and we only officially support lists anyway
                transformed[alias] = [
                    self._transform_aliases(data) if isinstance(data, dict) else data  # type: ignore
                    for data in value
                ]
            else:
                transformed[alias] = value
        return transformed


def _prisma_model_for_field(
    field: FieldInfo,
    *,
    name: str,
    parent: type[BaseModel],
) -> type[PrismaModel] | None:
    cls_name = parent.__name__
    type_ = model_field_type(field)
    if type_ is None:
        raise RuntimeError(f'Unexpected field type is None for {cls_name}.{name}')

    types: Iterable[type]
    if is_union(get_origin(type_)):
        types = get_args(type_)
    else:
        types = [type_]

    for type_ in types:
        if isinstance(type_, ForwardRef):
            raise RuntimeError(
                f'Encountered forward reference for {cls_name}.{name}; Forward references must be evaluated using {cls_name}.update_forward_refs()'
            )

        if is_list_type(type_) and type_ is not None:
            type_ = get_args(type_)[0]

        if hasattr(type_, '__prisma_model__'):
            return type_

    return None


def _field_is_prisma_model(field: FieldInfo, *, name: str, parent: type[BaseModel]) -> bool:
    """Whether or not the given field info represents a model at the database level.
    This will return `True` for cases where the field represents a list of models or a single model.
    """
    return _prisma_model_for_field(field, name=name, parent=parent) is not None


def _is_prisma_model_type(type_: type[BaseModel]) -> TypeGuard[type[PrismaModel]]:
    from .bases import _PrismaModel  # noqa: TID251

    return issubclass(type_, _PrismaModel)


class AbstractNode(ABC):
    __slots__ = ()

    @abstractmethod
    def render(self) -> str | None:
        """Render the node to a string

        None is returned if the node should not be rendered.
        """
        ...

    def should_render(self) -> bool:
        """If True, rendering of the node is skipped

        Useful for some nodes as they should only actually
        be rendered if they have any children.
        """
        return True


class Node(AbstractNode):
    """Base node handling rendering of child nodes"""

    joiner: str
    indent: str
    builder: QueryBuilder
    children: list[ChildType]

    __slots__ = (
        'joiner',
        'indent',
        'builder',
        'children',
    )

    def __init__(
        self, builder: QueryBuilder, *, joiner: str = '\n', indent: str = '  ', children: list[ChildType] | None = None
    ) -> None:
        self.builder = builder
        self.joiner = joiner
        self.indent = indent
        self.children = children if children is not None else []

    def enter(self) -> str | None:
        """Get the string used to enter the node.

        This string will be rendered *before* the children.
        """
        return None

    def depart(self) -> str | None:
        """Get the string used to depart the node.

        This string will be rendered *after* the children.
        """
        return None

    @override
    def render(self) -> str | None:
        """Render the node and it's children and to string.

        Rendering a node involves 4 steps:

        1. Entering the node
        2. Rendering it's children
        3. Departing the node
        4. Joining the previous steps together into a single string
        """
        if not self.should_render():
            return None

        strings: list[str] = []
        entered = self.enter()
        if entered is not None:
            strings.append(entered)

        for child in self.children:
            content: str | None = None

            if isinstance(child, str):
                content = child
            else:
                content = child.render()

            if content:
                strings.append(indent(content, self.indent))

        departed = self.depart()
        if departed is not None:
            strings.append(departed)

        return self.joiner.join(strings)

    def add(self, child: ChildType) -> None:
        """Add a child"""
        self.children.append(child)

    def create_children(self) -> list[ChildType]:
        """Create the node's children

        If children are passed to the constructor, the children
        returned from this method are used to extend the already
        set children.
        """
        return []

    @classmethod
    def create(cls, builder: QueryBuilder | None = None, **kwargs: Any) -> 'Node':
        """Create the node and its children

        This is useful for subclasses that add extra attributes in __init__
        """
        kwargs.setdefault('builder', builder)
        node = cls(**kwargs)
        node.children.extend(node.create_children())
        return node


class RootNode(Node):
    """Rendered node examples:

    query {
        <children>
    }

    or

    mutation {
        <children>
    }
    """

    __slots__ = ()

    @override
    def enter(self) -> str:
        return f'{self.builder.operation} {{'

    @override
    def depart(self) -> str:
        return '}'

    @override
    def render(self) -> str:
        content = super().render()
        if not content:  # pragma: no cover
            # this should never happen.
            # render() is typed to return None if the node
            # should not be rendered but as this node will
            # always be rendered it should always return
            # a non-empty string.
            raise RuntimeError('Could not generate query.')
        return content


class ResultNode(Node):
    """Rendered node examples:

    result: findUniqueUser
        <children>

    or

    result: executeRaw
        <children>
    """

    __slots__ = ()

    def __init__(self, indent: str = '', **kwargs: Any) -> None:
        super().__init__(indent=indent, **kwargs)

    @override
    def enter(self) -> str:
        model = self.builder.model
        if model is not None:
            model_name = model.__prisma_model__
        else:
            model_name = ''

        method = self.builder.method_format.format(model=model_name)
        return f'result: {method}'

    @override
    def depart(self) -> str | None:
        return None

    @override
    def create_children(self) -> list[ChildType]:
        return [
            Arguments.create(
                self.builder,
                arguments=self.builder.arguments,
            )
        ]


class Arguments(Node):
    """Rendered node example:

    (
        key1: "1"
        key2: "[\"John\",\"123\"]"
        key3: true
        key4: {
            data: true
        }
    )
    """

    arguments: dict[str, Any]

    __slots__ = ('arguments',)

    def __init__(self, arguments: dict[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.arguments = arguments

    @override
    def should_render(self) -> bool:
        return bool(self.children)

    @override
    def enter(self) -> str:
        return '('

    @override
    def depart(self) -> str:
        return ')'

    @override
    def create_children(self, arguments: dict[str, Any] | None = None) -> list[ChildType]:
        children: list[ChildType] = []

        for arg, value in self.arguments.items():
            if value is None:
                # ignore None values for convenience
                continue

            if isinstance(value, dict):
                children.append(Key(arg, node=Data.create(self.builder, data=value)))
            elif isinstance(value, ITERABLES):
                # NOTE: we have a special case for execute_raw, query_raw and query_first
                # here as prisma expects parameters to be passed as a json string
                # value like "[\"John\",\"123\"]", and we encode twice to ensure
                # that only the inner quotes are escaped
                if self.builder.method in {'query_raw', 'query_first', 'execute_raw'}:
                    children.append(f'{arg}: {dumps(dumps(value))}')
                else:
                    children.append(Key(arg, node=ListNode.create(self.builder, data=value)))
            else:
                children.append(f'{arg}: {dumps(value)}')

        return children


class Data(Node):
    """Rendered node example:

    {
        key1: "a"
        key2: 3
        key3: [
            "name"
        ]
    }
    """

    data: Mapping[str, Any]

    __slots__ = ('data',)

    def __init__(self, data: Mapping[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.data = data

    @override
    def enter(self) -> str:
        return '{'

    @override
    def depart(self) -> str:
        return '}'

    @override
    def create_children(self) -> list[ChildType]:
        children: list[ChildType] = []

        for key, value in self.data.items():
            if isinstance(value, dict):
                children.append(Key(key, node=Data.create(self.builder, data=value)))
            elif isinstance(value, (list, tuple, set)):
                children.append(Key(key, node=ListNode.create(self.builder, data=value)))
            else:
                children.append(f'{key}: {dumps(value)}')

        return children


class ListNode(Node):
    data: Iterable[Any]

    __slots__ = ('data',)

    def __init__(self, data: Iterable[Any], joiner: str = ',\n', **kwargs: Any) -> None:
        super().__init__(joiner=joiner, **kwargs)
        self.data = data

    @override
    def enter(self) -> str:
        return '['

    @override
    def depart(self) -> str:
        return ']'

    @override
    def create_children(self) -> list[ChildType]:
        children: list[ChildType] = []

        for item in self.data:
            if isinstance(item, dict):
                children.append(Data.create(self.builder, data=item))
            else:
                children.append(dumps(item))

        return children


class Selection(Node):
    """Represents field selections

    Example no include:

    {
        id
        name
    }

    Example include={'posts': True}

    {
        id
        name
        posts {
            id
            title
        }
    }

    Example include={'posts': {'where': {'title': {'contains': 'Test'}}}}

    {
        id
        name
        posts(
            where: {
                title: {
                    contains: 'Test'
                }
            }
        )
        {
            id
            title
        }
    }
    """

    model: type[MetaFieldsInterface] | None
    include: dict[str, Any] | None
    root_selection: list[str] | None

    __slots__ = (
        'model',
        'include',
        'root_selection',
    )

    def __init__(
        self,
        model: type[MetaFieldsInterface] | None = None,
        include: dict[str, Any] | None = None,
        root_selection: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model = model
        self.include = include
        self.root_selection = root_selection

    @override
    def should_render(self) -> bool:
        return bool(self.children)

    @override
    def enter(self) -> str:
        return '{'

    @override
    def depart(self) -> str:
        return '}'

    @override
    def create_children(self) -> list[ChildType]:
        model = self.model
        include = self.include
        builder = self.builder
        children: list[ChildType] = []

        # root_selection, if present overrides the default fields
        # for a model as it is used by methods such as count()
        # that do not support returning model fields
        root_selection = self.root_selection
        if root_selection is not None:
            children.extend(root_selection)
        elif model is not None:
            if hasattr(model, 'get_meta_fields'):
                for field, info in model.get_meta_fields().items():
                    children.append(self._get_child_from_model(field, info))
            else:
                children.extend(builder.get_default_fields(model))  # type: ignore

        if include is not None:
            if model is None:
                raise ValueError('Cannot include fields when model is None.')

            if not isinstance(model, type(BaseModel)):
                raise ValueError(f'Expected model to be a Pydantic model but got {type(model)} instead.')
            model = cast(type[BaseModel], model)

            for key, value in include.items():
                if value is True:
                    # e.g. posts { post_fields }
                    children.append(
                        Key(
                            key,
                            sep=' ',
                            node=Selection.create(
                                builder,
                                include=None,
                                model=builder.get_relational_model(current_model=model, field=key),
                            ),
                        )
                    )
                elif isinstance(value, dict):
                    # e.g. given {'posts': {where': {'published': True}}} return
                    # posts( where: { published: true }) { post_fields }
                    args = value.copy()
                    nested_include = args.pop('include', None)
                    children.extend(
                        [
                            Key(
                                key,
                                sep='',
                                node=Arguments.create(builder, arguments=args),
                            ),
                            Selection.create(
                                builder,
                                include=nested_include,
                                model=builder.get_relational_model(current_model=model, field=key),
                            ),
                        ]
                    )
                elif value is False:
                    continue
                else:
                    raise TypeError(f'Expected `bool` or `dict` include value but got {type(value)} instead.')

        return children

    def _get_child_from_model(self, field: str, info: PartialModelField) -> ChildType:
        builder = self.builder

        composite_type = info.get('composite_type')

        if composite_type is not None:
            return Key(
                field,
                sep=' ',
                node=Selection.create(
                    builder,
                    include=None,
                    model=composite_type,
                ),
            )

        if info.get('is_relational'):
            return ''

        return field


class Key(AbstractNode):
    """Node for rendering a child node with a prefixed key"""

    key: str
    sep: str
    node: Node

    __slots__ = (
        'key',
        'sep',
        'node',
    )

    def __init__(self, key: str, node: Node, sep: str = ': ') -> None:
        self.key = key
        self.node = node
        self.sep = sep

    @override
    def render(self) -> str:
        content = self.node.render()
        if content:
            return f'{self.key}{self.sep}{content}'
        return f'{self.key}{self.sep}'


@singledispatch
def serializer(obj: Any) -> Serializable:
    """Single dispatch generic function for serializing objects to JSON"""
    if inspect.isclass(obj):
        typ = obj
    else:
        typ = type(obj)

    raise TypeError(f'Type {typ} not serializable')


@serializer.register(datetime.datetime)
def serialize_datetime(dt: datetime.datetime) -> str:
    """Format a datetime object to an ISO8601 string with a timezone.

    This assumes naive datetime objects are in UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        dt = dt.astimezone(timezone.utc)

    # truncate microseconds to 3 decimal places
    # https://github.com/RobertCraigie/prisma-client-py/issues/129
    dt = dt.replace(microsecond=int(dt.microsecond / 1000) * 1000)
    return dt.isoformat()


@serializer.register(fields.Json)
def serialize_json(obj: fields.Json) -> str:
    """Serialize a Json wrapper to a json string.

    This is used as a hook to override our default behaviour when building
    queries which would treat data like {'hello': 'world'} as a Data node
    when we instead want it to be rendered as a raw json string.

    This should only be used for fields that are of the `Json` type.
    """
    return dumps(obj.data)


@serializer.register(fields.Base64)
def serialize_base64(obj: fields.Base64) -> str:
    """Serialize a Base64 wrapper object to raw binary data"""
    return str(obj)


@serializer.register(decimal.Decimal)
def serialize_decimal(obj: decimal.Decimal) -> str:
    """Serialize a Decimal object to a string"""
    return str(obj)


def dumps(obj: Any, **kwargs: Any) -> str:
    kwargs.setdefault('default', serializer)
    kwargs.setdefault('ensure_ascii', False)
    return json.dumps(obj, **kwargs)


# black does not respect the fmt: off comment without this
# fmt: on
