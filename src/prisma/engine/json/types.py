from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict

type JsonQueryAction = Literal[
    'findUnique',
    'findUniqueOrThrow',
    'findFirst',
    'findFirstOrThrow',
    'findMany',
    'createOne',
    'createMany',
    'createManyAndReturn',
    'updateOne',
    'updateMany',
    'deleteOne',
    'deleteMany',
    'upsertOne',
    'aggregate',
    'groupBy',
    'executeRaw',
    'queryRaw',
    'runCommandRaw',
    'findRaw',
    'aggregateRaw',
]


DateTaggedValue = TypedDict('DateTaggedValue', {'$type': Literal['DateTime'], 'value': str})
DecimalTaggedValue = TypedDict('DecimalTaggedValue', {'$type': Literal['Decimal'], 'value': str})
BytesTaggedValue = TypedDict('BytesTaggedValue', {'$type': Literal['Bytes'], 'value': str})
BigIntTaggedValue = TypedDict('BigIntTaggedValue', {'$type': Literal['BigInt'], 'value': str})
_FieldRefTaggedValue = TypedDict('_FieldRefTaggedValue', {'_ref': str, '_container': str})
FieldRefTaggedValue = TypedDict(
    'FieldRefTaggedValue',
    {'$type': Literal['FieldRef'], 'value': _FieldRefTaggedValue},
)
EnumTaggedValue = TypedDict('EnumTaggedValue', {'$type': Literal['Enum'], 'value': str})
JsonTaggedValue = TypedDict('JsonTaggedValue', {'$type': Literal['Json'], 'value': str})
RawTaggedValue = TypedDict('RawTaggedValue', {'$type': Literal['Raw'], 'value': Any})

type JsonInputTaggedValue = (
    DateTaggedValue
    | DecimalTaggedValue
    | BytesTaggedValue
    | BigIntTaggedValue
    | FieldRefTaggedValue
    | JsonTaggedValue
    | EnumTaggedValue
    | RawTaggedValue
)

type JsonOutputTaggedValue = (
    DateTaggedValue | DecimalTaggedValue | BytesTaggedValue | BigIntTaggedValue | JsonTaggedValue
)


type JsonArgumentValue = (
    int | str | bool | None | RawTaggedValue | list[JsonArgumentValue] | dict[str, JsonArgumentValue]
)


_JsonSelectionSet = TypedDict(
    '_JsonSelectionSet',
    {
        '$scalars': bool,
        '$composites': bool,
    },
    total=False,
)
type JsonSelectionSet = _JsonSelectionSet | dict[str, bool | JsonFieldSelection]


class JsonFieldSelection(TypedDict):
    arguments: NotRequired[dict[str, JsonArgumentValue] | RawTaggedValue]
    selection: JsonSelectionSet


class JsonQuery(TypedDict):
    modelName: NotRequired[str]
    action: JsonQueryAction
    query: JsonFieldSelection


class _Transaction(TypedDict):
    isolationLevel: NotRequired[
        Literal[
            'ReadUncommitted',
            'ReadCommitted',
            'RepeatableRead',
            'Snapshot',
            'Serializable',
        ]
    ]


class JsonBatchQuery(TypedDict):
    batch: list[JsonQuery]
    transaction: NotRequired[_Transaction]
