import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from .engine import QueryEngine


class QueryBuilder(BaseModel):
    # prisma method
    method: str

    # GraphQL operation
    operation: str

    model: str
    engine: QueryEngine
    data: Dict[str, Any]
    fields_: List[str] = Field(alias='fields')

    class Config:
        arbitrary_types_allowed = True

    def build(self) -> str:
        data = {
            'variables': {},
            'operation_name': 'mutation',
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
              f'result: {self.method}{self.model}('
                f'data: {self.build_data()}'
              f'){{ {" ".join(self.fields_)} }}'
            '}'
        )
        # fmt: on

    def build_data(self) -> str:
        """Returns a custom json dumped string of a dictionary.

        differences:
        - Without quotes surrounding each key value
        - Ignore null values

        e.g. {'title': 'hi', 'published': False, 'desc': None} -> {title: "hi", published: false}
        """
        strings = []
        dumps = json.dumps
        for key, value in self.data.items():
            if value is not None:
                strings.append(f'{key}: {dumps(value)}')
        return f'{{ {", ".join(strings)} }}'

    async def execute(self) -> Any:
        payload = self.build()
        return await self.engine.request('POST', '/', data=payload)
