from __future__ import annotations

from inline_snapshot import snapshot

from prisma.generator import parse_schema_dsl


def test_with_single_arg() -> None:
    assert parse_schema_dsl("""@Python(name: "UserFoo")""") == snapshot(
        {'type': 'ok', 'value': {'arguments': {'name': 'UserFoo'}}}
    )


def test_with_multiple_args() -> None:
    assert parse_schema_dsl("""@Python(name: "UserFoo", instance_name: "user_foo")""") == snapshot(
        {'type': 'ok', 'value': {'arguments': {'name': 'UserFoo', 'instance_name': 'user_foo'}}}
    )


def test_string_value_no_quotes() -> None:
    assert parse_schema_dsl("""@Python(name: UserFoo)""") == snapshot(
        {
            'type': 'invalid',
            'error': """\
Unexpected token Token('CNAME', 'UserFoo') at line 1, column 15.
Expected one of: 
	* ESCAPED_STRING
Previous tokens: [Token('COLON', ':')]
@Python(name: UserFoo)
              ^
""",
        }
    )


def test_string_value_double_quotes() -> None:
    assert parse_schema_dsl("""@Python(name: "UserFoo")""") == snapshot(
        {'type': 'ok', 'value': {'arguments': {'name': 'UserFoo'}}}
    )


def test_string_value_single_quotes() -> None:
    assert parse_schema_dsl("""@Python(name: 'UserFoo')""") == snapshot(
        {'type': 'ok', 'value': {'arguments': {'name': 'UserFoo'}}}
    )


def test_with_number_arg() -> None:
    assert parse_schema_dsl("""@Python(foo: 1)""") == snapshot(
        {
            'type': 'invalid',
            'error': """\
No terminal matches '1' in the current parser context, at line 1 col 14

@Python(foo: 1)
             ^
Expected one of: 
	* ESCAPED_STRING

Previous tokens: Token('COLON', ':')
@Python(foo: 1)
             ^
""",
        }
    )


def test_no_args() -> None:
    assert parse_schema_dsl("""@Python()""") == snapshot({'type': 'not_applicable'})


def test_no_pattern() -> None:
    assert parse_schema_dsl("""foo bar baz!""") == snapshot({'type': 'not_applicable'})


def test_at_symbol_different_ident() -> None:
    assert parse_schema_dsl("""@Foo(bar: baz)""") == snapshot({'type': 'not_applicable'})


def test_multiple() -> None:
    assert parse_schema_dsl(
        """
        @Python(bar: baz)
        @Python(foo: bar)
    """
    ) == snapshot({'type': 'invalid', 'error': 'Encountered multiple `@Python` declarations'})


def test_missing_arg_colon_sep() -> None:
    assert parse_schema_dsl("""@Python(name "UserFoo")""") == snapshot(
        {
            'type': 'invalid',
            'error': """\
Unexpected token Token('ESCAPED_STRING', '"UserFoo"') at line 1, column 14.
Expected one of: 
	* COLON
Previous tokens: [Token('CNAME', 'name')]
@Python(name "UserFoo")
             ^
""",
        }
    )


def test_with_arbitrary_surrounding_text() -> None:
    assert parse_schema_dsl("""foo bar! () @Python(name: 'UserFoo') baz bing 18738/.m{]}""") == snapshot(
        {'type': 'ok', 'value': {'arguments': {'name': 'UserFoo'}}}
    )


def test_error_with_arbitrary_surrounding_text() -> None:
    assert parse_schema_dsl("""foo bar! () @Python(name 'UserFoo') baz bing 18738/.m{]}""") == snapshot(
        {
            'type': 'invalid',
            'error': """\
Unexpected token Token('ESCAPED_STRING', "'UserFoo'") at line 1, column 14.
Expected one of: 
	* COLON
Previous tokens: [Token('CNAME', 'name')]
@Python(name 'UserFoo')
             ^
""",
        }
    )
