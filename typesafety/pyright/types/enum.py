from prisma import Prisma
from prisma.enums import Role


async def filtering(client: Prisma) -> None:
    # case: all valid filter fields
    await client.types.find_first(
        where={
            'role': Role.USER,
        },
    )


def use_str_enum_as_str():
    # case: StrEnum is compatible with str typing
    _test_string: str = Role.USER


def raise_error_on_invalid_type():
    _test_int: int = Role.USER  # E: Expression of type "Literal[Role.USER]" cannot be assigned to declared type "int"
