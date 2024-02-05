"""Lark parser for our custom DSL inside Prisma Schemas, e.g.

```prisma
/// @Python(name: foo)
model bar {
  // ...
}
```
"""
from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypedDict

from .transformer import TransformResult, DefinitionTransformer
from ..._vendor.lark_schema_parser import Lark_StandAlone as LarkParser, UnexpectedInput
from ..._vendor.lark_schema_scan_parser import Lark_StandAlone as LarkScanner

scanner = LarkScanner()  # type: ignore[no-untyped-call]
schema_extension_parser = LarkParser()  # type: ignore[no-untyped-call]

transformer = DefinitionTransformer()


def parse_schema_dsl(text: str) -> ParseResult:
    """Given a string like `@Python(foo: bar)`
    returns `{ 'type': 'ok', 'value': { 'arguments': { 'foo': 'bar' } } }`.

    If the string is not valid syntax, then `{'type': 'invalid', 'error': 'msg'}`
    is returned.

    If the string is not actually even attempting to represent the `@Python`
    DSL, then `{'type': 'not_applicable'}` is returned.

    Note, currently `not_applicable` will be returned if there are no arguments given
    to `@Python`, e.g. `@Python()`. This currently doesn't matter, but it may be changed
    in the future.
    """
    parts = scan_for_declarations(text)
    if not parts:
        return {'type': 'not_applicable'}

    if len(parts) > 1:
        # TODO: include context in error message
        return {'type': 'invalid', 'error': f'Encountered multiple `@Python` declarations'}

    start, end = parts[0]

    snippet = text[start:end]

    try:
        parsed = schema_extension_parser.parse(snippet)
    except UnexpectedInput as exc:
        return {'type': 'invalid', 'error': str(exc) + exc.get_context(snippet)}

    transformed = transformer.transform(parsed)
    return {'type': 'ok', 'value': transformed}


def scan_for_declarations(text: str) -> list[tuple[int, int]]:
    """Returns a list of (start, end) of parts of the text that
    look like `@Python(...)`.

    Note: this is just needed until Lark provides a more complete
    way to scan for a grammar and also provide syntax errors.

    https://github.com/lark-parser/lark/discussions/1390#discussioncomment-8354420
    """
    return [indices for indices, _ in scanner.scan(text)]


class ParseResultOk(TypedDict):
    type: Literal['ok']
    value: TransformResult


class ParseResultInvalid(TypedDict):
    type: Literal['invalid']
    error: str


class ParseResultNotApplicable(TypedDict):
    type: Literal['not_applicable']


ParseResult = Union[ParseResultOk, ParseResultInvalid, ParseResultNotApplicable]
