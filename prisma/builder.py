import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from .engine import QueryEngine


class QueryBuilder(BaseModel):
    # prisma method
    method: str

    # GraphQL operation
    operation: str

    model: Optional[str]
    engine: QueryEngine
    arguments: Dict[str, Any]
    fields_: Optional[List[str]] = Field(alias='fields')

    class Config:
        arbitrary_types_allowed = True

    def build(self) -> str:
        data = {
            'variables': {},
            'operation_name': self.operation,
            'query': self.build_query(),
        }
        return json.dumps(data)

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
              f'result: {self.method}{self.model if self.model else ""}('
                f'{self.build_args()}'
              f'){self.build_fields()}'
            '}'
        )
        # fmt: on

    def build_args(self) -> str:
        """Returns a string representing the arguments to the the GraphQL query.

        e.g. 'where: { id: "hsdajkd2" } take: 1'
        """
        strings = []
        for arg, value in self.arguments.items():
            if isinstance(value, dict):
                parsed = self.build_data(value)
            elif isinstance(value, (list, tuple)):
                # prisma expects a json string value like "[\"John\",\"123\"]"
                # we encode twice to ensure that only the inner quotes are escaped
                # yes this is a terrible solution
                # TODO: better solution
                parsed = json.dumps(json.dumps(value))
            else:
                parsed = json.dumps(value)

            strings.append(f'{arg}: {parsed}')

        return ' '.join(strings)

    def build_fields(self) -> str:
        if self.fields_ is None:
            return ''

        return f'{{ {" ".join(self.fields_)} }}'

    def build_data(self, data: Dict[str, Any]) -> str:
        """Returns a custom json dumped string of a dictionary.

        differences:
        - Without quotes surrounding each key value
        - Ignore null values

        e.g. {'title': 'hi', 'published': False, 'desc': None} -> {title: "hi", published: false}
        """
        strings = []
        dumps = json.dumps
        for key, value in data.items():
            if value is not None:
                strings.append(f'{key}: {dumps(value)}')

        return f'{{ {", ".join(strings)} }}'

    async def execute(self) -> Any:
        payload = self.build()
        return await self.engine.request('POST', '/', data=payload)
