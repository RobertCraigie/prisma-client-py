import pytest
from pydantic import ValidationError
from syrupy.assertion import SnapshotAssertion

from prisma import validate, types


class Foo:
    pass


def test_valid() -> None:
    """Basic usage with correct data"""
    validated = validate(types.IntFilter, {'equals': 1})
    assert validated == {'equals': 1}

    validated = validate(types.IntFilter, {'equals': '1'})
    assert validated == {'equals': 1}


def test_disallows_non_typeddict_type(snapshot: SnapshotAssertion) -> None:
    """Validating against non TypedDict types throws an error"""
    with pytest.raises(TypeError) as exc:
        validate(Foo, None)

    assert str(exc.value) == snapshot

    with pytest.raises(TypeError) as exc:
        validate(dict, None)

    assert str(exc.value) == snapshot


def test_non_dictionary_values(snapshot: SnapshotAssertion) -> None:
    """Validating a non-dictionary value throws an error"""
    with pytest.raises(ValidationError) as exc:
        validate(types.UserCreateInput, None)

    assert str(exc.value) == snapshot


def test_recursive(snapshot: SnapshotAssertion) -> None:
    """Validating recursive types works as expected"""
    with pytest.raises(ValidationError) as exc:
        validate(types.FloatFilter, {'not': {'not': {'not': 'a'}}})

    assert str(exc.value) == snapshot

    validated = validate(types.FloatFilter, {'not': {'not': {'not': '193.4'}}})
    assert validated == {'not': {'not': {'not': 193.4}}}


def test_missing_values(snapshot: SnapshotAssertion) -> None:
    """TypedDict with required keys is correctly validated"""
    with pytest.raises(ValidationError) as exc:
        validate(types.PostCreateInput, {})

    assert str(exc.value) == snapshot


def test_optional_values() -> None:
    """Fields that can be None are still included in the validated data"""
    validated = validate(
        types.PostCreateInput, dict(title='My Title', published=True)
    )
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


def test_disallows_extra_values(snapshot: SnapshotAssertion) -> None:
    """Fields that are not present in the TypedDict are not allowed"""
    with pytest.raises(ValidationError) as exc:
        validate(types.PostCreateInput, {'foo': 'bar'})

    assert str(exc.value) == snapshot
