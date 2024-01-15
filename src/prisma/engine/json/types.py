# taken from https://github.com/prisma/prisma/blob/main/packages/engine-core/src/common/types/JsonProtocol.ts
from typing import Union
from typing_extensions import Literal, TypedDict


DateTaggedValue = TypedDict(
    'DateTaggedValue',
    {
        '$type': Literal['DateTime'],
        'value': str,
    },
)

DecimalTaggedValue = TypedDict(
    'DecimalTaggedValue',
    {
        '$type': Literal['Decimal'],
        'value': str,
    },
)

BytesTaggedValue = TypedDict(
    'BytesTaggedValue',
    {
        '$type': Literal['Bytes'],
        'value': str,
    },
)

BigIntTaggedValue = TypedDict(
    'BigIntTaggedValue',
    {
        '$type': Literal['BigInt'],
        'value': str,
    },
)


class FieldRefValue(TypedDict):
    _ref: str


FieldRefTaggedValue = TypedDict(
    'FieldRefTaggedValue',
    {
        '$type': Literal['FieldRef'],
        'value': FieldRefValue,
    },
)

EnumTaggedValue = TypedDict(
    'EnumTaggedValue',
    {
        '$type': Literal['Enum'],
        'value': str,
    },
)

JsonTaggedValue = TypedDict(
    'JsonTaggedValue',
    {
        '$type': Literal['Json'],
        'value': str,
    },
)


OutputTaggedValue = Union[
    DateTaggedValue,
    EnumTaggedValue,
    JsonTaggedValue,
    BytesTaggedValue,
    BigIntTaggedValue,
    DecimalTaggedValue,
    FieldRefTaggedValue,
]
