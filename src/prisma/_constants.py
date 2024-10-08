from typing import Dict
from datetime import timedelta

DEFAULT_CONNECT_TIMEOUT: timedelta = timedelta(seconds=10)
DEFAULT_TX_MAX_WAIT: timedelta = timedelta(milliseconds=2000)
DEFAULT_TX_TIMEOUT: timedelta = timedelta(milliseconds=5000)

# key aliases to transform query arguments to make them more pythonic
QUERY_BUILDER_ALIASES: Dict[str, str] = {
    'startswith': 'startsWith',
    'has_every': 'hasEvery',
    'endswith': 'endsWith',
    'has_some': 'hasSome',
    'is_empty': 'isEmpty',
    'order_by': 'orderBy',
    'not_in': 'notIn',
    'is_not': 'isNot',
    'connect_or_create': 'connectOrCreate',
}

CREATE_MANY_SKIP_DUPLICATES_UNSUPPORTED = {'mongodb', 'sqlserver', 'sqlite'}
