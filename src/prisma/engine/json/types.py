from __future__ import annotations

from typing import Any, Dict, List, Union, Literal, TypedDict
from typing_extensions import NotRequired

JsonQueryAction = Literal[
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


JsonInputTaggedValue = Union[
    DateTaggedValue,
    DecimalTaggedValue,
    BytesTaggedValue,
    BigIntTaggedValue,
    FieldRefTaggedValue,
    JsonTaggedValue,
    EnumTaggedValue,
    RawTaggedValue,
]

JsonOutputTaggedValue = Union[
    DateTaggedValue,
    DecimalTaggedValue,
    BytesTaggedValue,
    BigIntTaggedValue,
    JsonTaggedValue,
]

JsonArgumentValue = Union[
    int,
    str,
    bool,
    None,
    RawTaggedValue,
    List['JsonArgumentValue'],
    Dict[str, 'JsonArgumentValue'],
]


class JsonFieldSelection(TypedDict):
    arguments: NotRequired[dict[str, JsonArgumentValue] | RawTaggedValue]
    selection: JsonSelectionSet


_JsonSelectionSet = TypedDict(
    '_JsonSelectionSet',
    {
        '$scalars': bool,
        '$composites': bool,
    },
    total=False,
)
JsonSelectionSet = Union[_JsonSelectionSet, Dict[str, Union[bool, JsonFieldSelection]]]


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
