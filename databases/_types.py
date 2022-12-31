from typing_extensions import Literal, TypedDict
from typing import Generic, TypeVar


_T = TypeVar('_T')


# NOTE: these must be lowercase as CLI arguments are converted to
# lowercase for ease of use.
#
# NOTE: if you update this, you must also update the `DatabaseMapping` type
SupportedDatabase = Literal[
    'mysql',
    'sqlite',
    'mariadb',
    'mongodb',
    'postgresql',
    'cockroachdb',
]


class DatabaseMapping(TypedDict, Generic[_T]):
    """Represents a mapping of database names to a generic type.

    This is useful to enforce that a mapping represents all valid database providers
    """

    mysql: _T
    sqlite: _T
    mariadb: _T
    mongodb: _T
    postgresql: _T
    cockroachdb: _T
