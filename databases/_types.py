from typing_extensions import Literal


# NOTE: these must be lowercase as CLI arguments are converted to
# lowercase for ease of use.
SupportedDatabase = Literal[
    'mysql',
    'sqlite',
    'mariadb',
    'postgresql',
    'cockroachdb',
]
