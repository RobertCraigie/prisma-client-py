from __future__ import annotations

import json
from typing import Any, Callable, overload
from typing_extensions import Literal

from ._types import BaseModelT
from ._compat import model_parse

# from https://github.com/prisma/prisma/blob/7da6f030350931eff8574e805acb9c0de9087e8e/packages/client/src/runtime/utils/deserializeRawResults.ts
PrismaType = Literal[
    'int',
    'bigint',
    'float',
    'double',
    'string',
    'enum',
    'bytes',
    'bool',
    'char',
    'decimal',
    'json',
    'xml',
    'uuid',
    'datetime',
    'date',
    'time',
    'int-array',
    'bigint-array',
    'float-array',
    'double-array',
    'string-array',
    'enum-array',
    'bytes-array',
    'bool-array',
    'char-array',
    'decimal-array',
    'json-array',
    'xml-array',
    'uuid-array',
    'datetime-array',
    'date-array',
    'time-array',
    'unknown-array',
    'unknown',
]


class RawQueryResult:
    columns: list[str]
    types: list[PrismaType]
    rows: list[list[object]]

    def __init__(
        self,
        *,
        columns: list[str],
        types: list[PrismaType],
        rows: list[list[object]],
    ) -> None:
        self.columns = columns
        self.types = types
        self.rows = rows


@overload
def deserialize_raw_results(raw_result: dict[str, Any]) -> list[dict[str, Any]]: ...


@overload
def deserialize_raw_results(
    raw_result: dict[str, Any],
    model: type[BaseModelT],
) -> list[BaseModelT]: ...


def deserialize_raw_results(
    raw_result: dict[str, Any],
    model: type[BaseModelT] | None = None,
) -> list[BaseModelT] | list[dict[str, Any]]:
    """Deserialize a list of raw query results into their rich Python types.

    If `model` is given, convert each result into the corresponding model.
    Otherwise results are returned as a dictionary
    """
    result = RawQueryResult(
        columns=raw_result['columns'],
        types=raw_result['types'],
        rows=raw_result['rows'],
    )
    if model is not None:
        return [_deserialize_prisma_object(obj, result=result, model=model, for_model=True) for obj in result.rows]

    return [_deserialize_prisma_object(obj, result=result, for_model=False) for obj in result.rows]


# NOTE: this very weird `for_model` API is simply here as a workaround for
# https://github.com/RobertCraigie/prisma-client-py/issues/638
#
# This should hopefully be removed soon.


@overload
def _deserialize_prisma_object(
    fields: list[object],
    *,
    result: RawQueryResult,
    for_model: bool,
) -> dict[str, Any]: ...


@overload
def _deserialize_prisma_object(
    fields: list[object],
    *,
    result: RawQueryResult,
    for_model: bool,
    model: type[BaseModelT],
) -> BaseModelT: ...


def _deserialize_prisma_object(
    fields: list[object],
    *,
    result: RawQueryResult,
    for_model: bool,
    model: type[BaseModelT] | None = None,
) -> BaseModelT | dict[str, Any]:
    # create a local reference to avoid performance penalty of global
    # lookups on some python versions
    _deserializers = DESERIALIZERS

    new_obj: dict[str, Any] = {}
    for i, field in enumerate(fields):
        key = result.columns[i]
        prisma_type = result.types[i]

        if field is None:
            new_obj[key] = None
            continue

        if prisma_type.endswith('-array'):
            if not isinstance(field, list):
                raise TypeError(
                    f'Expected array data for {key} column with internal type {prisma_type}',
                )

            item_type, _ = prisma_type.split('-')

            new_obj[key] = [
                _deserializers[item_type](value, for_model)
                #
                if item_type in _deserializers
                else value
                for value in field
            ]
        else:
            value = field

            new_obj[key] = _deserializers[prisma_type](value, for_model) if prisma_type in _deserializers else value

    if model is not None:
        return model_parse(model, new_obj)

    return new_obj


def _deserialize_bigint(value: str, _for_model: bool) -> int:
    return int(value)


def _deserialize_decimal(value: str, _for_model: bool) -> float:
    return float(value)


def _deserialize_json(value: object, for_model: bool) -> object:
    # TODO: this may break if someone inserts just a string into the database
    if not isinstance(value, str) and for_model:
        # TODO: this is very bad
        #
        # Pydantic expects Json fields to be a `str`, we should implement
        # an actual workaround for this validation instead of wasting compute
        # on re-serializing the data.
        return json.dumps(value)

    # This may or may not have already been deserialized by the database
    return value


DESERIALIZERS: dict[PrismaType, Callable[[Any, bool], object]] = {
    'bigint': _deserialize_bigint,
    'decimal': _deserialize_decimal,
    'json': _deserialize_json,
}
