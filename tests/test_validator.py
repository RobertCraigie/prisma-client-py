import pytest
from inline_snapshot import snapshot

from prisma import types, validate
from prisma._compat import PYDANTIC_V2


class Foo:
    pass


if PYDANTIC_V2:
    from pydantic.v1 import ValidationError
else:
    from pydantic import ValidationError  # type: ignore[assignment]


def test_valid() -> None:
    """Basic usage with correct data"""
    validated = validate(types.IntFilter, {'equals': 1})
    assert validated == {'equals': 1}

    validated = validate(types.IntFilter, {'equals': '1'})
    assert validated == {'equals': 1}


def test_disallows_non_typeddict_type() -> None:
    """Validating against non TypedDict types throws an error"""
    with pytest.raises(TypeError) as exc:
        validate(Foo, None)

    assert str(exc.value) == snapshot(
        "Only TypedDict types are supported, got: <class 'tests.test_validator.Foo'> instead."
    )

    with pytest.raises(TypeError) as exc:
        validate(dict, None)

    assert str(exc.value) == snapshot("Only TypedDict types are supported, got: <class 'dict'> instead.")


def test_non_dictionary_values() -> None:
    """Validating a non-dictionary value throws an error"""
    with pytest.raises(ValidationError) as exc:
        validate(types.UserCreateInput, None)

    assert str(exc.value) == snapshot(
        """\
1 validation error for UserCreateInput
__root__
  UserCreateInput expected dict not NoneType (type=type_error)\
"""
    )


def test_recursive() -> None:
    """Validating recursive types works as expected"""
    with pytest.raises(ValidationError) as exc:
        validate(types.FloatFilter, {'not': {'not': {'not': 'a'}}})

    assert str(exc.value) == snapshot(
        """\
4 validation errors for FloatFilter
not
  value is not a valid float (type=type_error.float)
not -> not
  value is not a valid float (type=type_error.float)
not -> not -> not
  value is not a valid float (type=type_error.float)
not -> not -> not -> __root__
  FloatFilterRecursive3 expected dict not str (type=type_error)\
"""
    )

    validated = validate(types.FloatFilter, {'not': {'not': {'not': '193.4'}}})
    assert validated == {'not': {'not': {'not': 193.4}}}


def test_missing_values() -> None:
    """TypedDict with required keys is correctly validated"""
    with pytest.raises(ValidationError) as exc:
        validate(types.PostCreateInput, {})

    assert str(exc.value) == snapshot(
        """\
2 validation errors for PostCreateInput
title
  field required (type=value_error.missing)
published
  field required (type=value_error.missing)\
"""
    )


def test_optional_values() -> None:
    """Fields that can be None are still included in the validated data"""
    validated = validate(types.PostCreateInput, dict(title='My Title', published=True))
    assert validated == {'title': 'My Title', 'published': True}

    validated = validate(
        type=types.PostCreateInput,
        data=dict(title='My Title', published=True, desc=None),
    )
    assert validated == {
        'title': 'My Title',
        'published': True,
        'desc': None,
    }


def test_disallows_extra_values() -> None:
    """Fields that are not present in the TypedDict are not allowed"""
    with pytest.raises(ValidationError) as exc:
        validate(types.PostCreateInput, {'foo': 'bar'})

    assert str(exc.value) == snapshot(
        """\
3 validation errors for PostCreateInput
title
  field required (type=value_error.missing)
published
  field required (type=value_error.missing)
foo
  extra fields not permitted (type=value_error.extra)\
"""
    )
