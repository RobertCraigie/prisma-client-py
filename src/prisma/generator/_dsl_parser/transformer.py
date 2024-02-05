from __future__ import annotations

from typing import Dict, cast
from typing_extensions import TypedDict

from ..._vendor.lark_schema_parser import Tree, Token, Transformer as LarkTransformer


class TransformResult(TypedDict):
    arguments: Arguments


Arguments = Dict[str, str]

ParseTree = Tree[Token]


class DefinitionTransformer(LarkTransformer[Token, TransformResult]):
    def start(self, items: tuple[ParseTree, Arguments | None]) -> TransformResult:
        _, args = items
        return {'arguments': args or {}}

    def argument_list(self, items: list[tuple[str, str] | None] | None) -> Arguments:
        if not items:
            return {}

        return {
            name: value
            for name, value in [
                # item can be None if there were no args passed
                item
                for item in items
                if item is not None
            ]
        }

    def argument(self, items: tuple[str, str]) -> tuple[str, str]:
        return items

    def key(self, items: tuple[Token]) -> str:
        return cast(str, items[0].value)

    def value(self, items: tuple[Token]) -> str:
        value = cast(str, items[0].value)

        if value.startswith(("'", '"')) and value.endswith(("'", '"')):
            return value[1:-1]
        return value
