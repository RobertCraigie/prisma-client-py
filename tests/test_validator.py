import pytest

# TODO: should we re-export this?
from pydantic import ValidationError
from syrupy import SnapshotAssertion

from prisma import validate, types


class Foo:
    pass


def test_simple() -> None:
    """TODO"""
    validated = validate(types.IntFilter, {'equals': 1})
    assert validated == {'equals': 1}

    validated = validate(types.IntFilter, {'equals': '1'})
    assert validated == {'equals': 1}


def test_disallows_non_typeddict_type(snapshot: SnapshotAssertion) -> None:
    """TODO"""
    with pytest.raises(TypeError) as exc:
        validate(Foo, None)  # type: ignore

    assert str(exc.value) == snapshot

    with pytest.raises(TypeError) as exc:
        validate(dict, None)  # type: ignore

    assert str(exc.value) == snapshot


def test_non_dictionary_values(snapshot: SnapshotAssertion) -> None:
    """TODO"""
    with pytest.raises(ValidationError) as exc:
        validate(types.UserCreateInput, None)

    assert str(exc.value) == snapshot


def test_recursive(snapshot: SnapshotAssertion) -> None:
    """TODO"""
    with pytest.raises(ValidationError) as exc:
        validate(types.FloatFilter, {'NOT': {'NOT': {'NOT': 'a'}}})

    assert str(exc.value) == snapshot

    validated = validate(types.FloatFilter, {'NOT': {'NOT': {'NOT': 193.4}}})
    assert validated == {'NOT': {'NOT': {'NOT': 193.4}}}
    assert validated == snapshot


def test_missing_values(snapshot: SnapshotAssertion) -> None:
    """TODO"""
    with pytest.raises(ValidationError) as exc:
        validate(types.PostCreateInput, {})

    assert str(exc.value) == snapshot


def test_optional_values() -> None:
    """Fields that can be None are still included in the validated data"""
    validated = validate(types.PostCreateInput, dict(title='My Title', published=True))
    assert validated == {'title': 'My Title', 'published': True}

    validated = validate(
        types.PostCreateInput, dict(title='My Title', published=True, desc=None)
    )
    assert validated == {'title': 'My Title', 'published': True, 'desc': None}
