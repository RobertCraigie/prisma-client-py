from typing import Any, cast

import pytest
from pydantic import Extra, BaseConfig, ValidationError, annotated_types
from syrupy.assertion import SnapshotAssertion

import prisma
from prisma import Client, validate, types


class Foo:
    pass


def test_valid() -> None:
    """Basic usage with correct data"""
    validated = validate(types.IntFilter, {'equals': 1})
    assert validated == {'equals': 1}  # type: ignore[comparison-overlap]

    validated = validate(types.IntFilter, {'equals': '1'})
    assert validated == {'equals': 1}  # type: ignore[comparison-overlap]


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
    assert validated == {'not': {'not': {'not': 193.4}}}  # type: ignore[comparison-overlap]


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
    assert validated == {'title': 'My Title', 'published': True}  # type: ignore[comparison-overlap]

    validated = validate(
        type=types.PostCreateInput,
        data=dict(title='My Title', published=True, desc=None),
    )
    assert validated == {  # type: ignore[comparison-overlap]
        'title': 'My Title',
        'published': True,
        'desc': None,
    }


def test_disallows_extra_values(snapshot: SnapshotAssertion) -> None:
    """Fields that are not present in the TypedDict are not allowed"""
    with pytest.raises(ValidationError) as exc:
        validate(types.PostCreateInput, {'foo': 'bar'})

    assert str(exc.value) == snapshot


class AllowExtraConfig(BaseConfig):
    extra: Extra = Extra.allow


class DisallowExtraConfig(BaseConfig):
    extra: Extra = Extra.forbid


def test_patch_respects_arguments(snapshot: SnapshotAssertion) -> None:
    """Ensure that creating a BaseModel from a TypedDict does not cache
    the BaseModel irrespective of the given __config__
    """
    Model = cast(
        Any,
        annotated_types.create_model_from_typeddict(
            types.UserCreateInput, __config__=AllowExtraConfig  # type: ignore
        ),
    )
    with pytest.raises(ValidationError) as exc:
        Model()

    assert str(exc.value) == snapshot

    model = Model(name='Robert')
    assert model.name == 'Robert'

    model = Model(name='Tegan', foo='bar')
    assert model.name == 'Tegan'
    assert model.foo == 'bar'

    Model = cast(
        Any,
        annotated_types.create_model_from_typeddict(
            types.UserCreateInput, __config__=DisallowExtraConfig  # type: ignore
        ),
    )
    with pytest.raises(ValidationError) as exc:
        Model(name='Robert', foo='bar')

    assert str(exc.value) == snapshot


@pytest.mark.asyncio
async def test_validate_arguments(
    client: Client,
    snapshot: SnapshotAssertion,
) -> None:
    """Ensure that passing incorrect arguments to an action method will raise a ValidationError"""
    with pytest.raises(ValidationError) as exc:
        await client.user.create({})  # type: ignore

    assert str(exc.value) == snapshot


@pytest.mark.asyncio
async def test_disable_validation(client: Client) -> None:
    """Ensure that query argument validation can be skipped"""
    with prisma.disable_validation():
        with pytest.raises(prisma.errors.MissingRequiredValueError):
            await client.user.create({})  # type: ignore


@pytest.mark.asyncio
async def test_nested_disable_validation(client: Client) -> None:
    """Ensure that nesting two disable_validation calls
    does not reset state prematurely
    """
    with prisma.disable_validation():
        with prisma.disable_validation():
            with pytest.raises(prisma.errors.MissingRequiredValueError):
                await client.user.create({})  # type: ignore

        with pytest.raises(prisma.errors.MissingRequiredValueError):
            await client.user.create({})  # type: ignore
