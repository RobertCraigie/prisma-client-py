import json
import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from .engine import QueryEngine


GLOBAL_ALIASES = {
    'startswith': 'startsWith',
    'endswith': 'endsWith',
    'order_by': 'orderBy',
    'not_in': 'notIn',
    'NOT': 'not',
    'IN': 'in',
}


class QueryBuilder(BaseModel):
    # prisma method
    method: str

    # GraphQL operation
    operation: str

    model: Optional[str]
    engine: QueryEngine
    arguments: Dict[str, Any]
    include: Optional[Dict[str, Any]]
    root_selection: Optional[List[str]]

    # mappings of model user facing fields to their corresponding query engine fields
    # an empty key represents the fields for the current model
    aliases: Optional[Dict[str, Dict[str, str]]]

    class Config:
        arbitrary_types_allowed = True

    def build(self) -> str:
        data = {
            'variables': {},
            'operation_name': self.operation,
            'query': self.build_query(),
        }
        return dumps(data)

    def build_query(self) -> str:
        """Build the GraphQL query string for this operation.

        e.g the following without newlines

        mutation {
          result: createOnePost(
            data: {
              title: "Hi from Prisma!"
              published: true
              desc: "Prisma is a database toolkit that makes databases easy."
            }
          ) { id published createdAt updatedAt title desc }
        }
        """
        # fmt: off
        return (
            f'{self.operation} {{'
              f'result: {self.method}{self.model if self.model else ""}{self.build_args()}'
                f'{self.build_fields()}'
            '}'
        )
        # fmt: on

    def build_args(
        self, arguments: Optional[Dict[str, Any]] = None, context: Optional[str] = None
    ) -> str:
        """Returns a string representing the arguments to the the GraphQL query.

        e.g. 'where: { id: "hsdajkd2" } take: 1'
        """
        if arguments is None:
            arguments = self.arguments

        strings = []
        args = self._transform_aliases(arguments, context)
        for arg, value in args.items():
            if isinstance(value, dict):
                parsed = self.build_data(value)
            elif isinstance(value, (list, tuple)):
                # prisma expects a json string value like "[\"John\",\"123\"]"
                # we encode twice to ensure that only the inner quotes are escaped
                # yes this is a terrible solution
                # TODO: better solution
                parsed = dumps(dumps(value))
            else:
                parsed = dumps(value)

            strings.append(f'{arg}: {parsed}')

        return f'({" ".join(strings)})' if strings else ''

    def build_fields(
        self, include: Optional[Dict[str, Any]] = None, context: Optional[str] = None
    ) -> str:
        aliases = self.aliases
        if aliases is None:
            return ''

        if context is None:
            context = ''

        if include is None:
            include = self.include

        fields = (
            self.root_selection.copy()
            if self.root_selection
            else list(aliases[context].values())
        )
        if include is None:
            return f'{{ {" ".join(fields)} }}'

        for key, value in include.items():
            if value is True:
                fields.append(f'{key} {{ {" ".join(aliases[key].values())} }}')
            elif value is False:
                continue
            elif isinstance(value, dict):
                args = value.copy()
                nested_include = args.pop('include', {})
                fields.append(
                    f'{key}{self.build_args(args, context=key)} '
                    f'{self.build_fields(include=nested_include, context=key)}'
                )
            else:
                raise TypeError(
                    f'Expected `bool` or `dict` include value but got {type(value)} instead'
                )

        return f'{{ {" ".join(fields)} }}'

    def build_data(self, data: Dict[str, Any], transform: Optional[bool] = True) -> str:
        """Returns a custom json dumped string of a dictionary.

        differences:
        - Without quotes surrounding each key value
        - Ignore null values

        e.g. {'title': 'hi', 'published': False, 'desc': None} -> {title: "hi", published: false}
        """
        strings = []

        if transform:
            transformed = self._transform_aliases(data)
        else:
            # aliases have already been transformed
            transformed = data

        for key, value in transformed.items():
            if value is None:
                continue

            if isinstance(value, dict):
                strings.append(f'{key}: {self.build_data(value, transform=False)}')
            elif isinstance(value, (list, tuple)):
                inner = []
                for item in value:
                    if isinstance(item, dict):
                        inner.append(self.build_data(item, transform=False))
                    else:
                        inner.append(dumps(item))
                strings.append(f'{key}: [{", ".join(inner)}]')
            else:
                strings.append(f'{key}: {dumps(value)}')

        return f'{{ {", ".join(strings)} }}'

    def _transform_aliases(
        self, data: Dict[str, Any], context: Optional[str] = None
    ) -> Dict[str, Any]:
        if self.aliases is None:
            return data

        mappings = self.aliases.get(context if context is not None else '')
        if mappings is None:
            return data

        transformed = {}  # type: Dict[str, Any]
        for inner_key, value in data.items():
            alias = mappings.get(inner_key, GLOBAL_ALIASES.get(inner_key, inner_key))
            if isinstance(value, dict):
                transformed[alias] = self._transform_aliases(
                    value,
                    context=inner_key if inner_key in self.aliases.keys() else context,
                )
            else:
                transformed[alias] = value
        return transformed

    async def execute(self) -> Any:
        payload = self.build()
        return await self.engine.request('POST', '/', data=payload)


def serialize_json(obj: Any) -> str:
    """JSON serializer for objects not serializable by the default JSON encoder"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    raise TypeError(f'Type {type(obj)} not serializable')


def dumps(obj: Any, **kwargs: Any) -> str:
    kwargs.setdefault('default', serialize_json)
    return json.dumps(obj, **kwargs)
