from typing import Any, Dict
from datetime import timedelta

import httpx

DEFAULT_CONNECT_TIMEOUT: timedelta = timedelta(seconds=10)
DEFAULT_TX_MAX_WAIT: timedelta = timedelta(milliseconds=2000)
DEFAULT_TX_TIMEOUT: timedelta = timedelta(milliseconds=5000)

DEFAULT_HTTP_LIMITS: httpx.Limits = httpx.Limits(max_connections=1000)
DEFAULT_HTTP_TIMEOUT: httpx.Timeout = httpx.Timeout(30)
DEFAULT_HTTP_CONFIG: Dict[str, Any] = {
    'limits': DEFAULT_HTTP_LIMITS,
    'timeout': DEFAULT_HTTP_TIMEOUT,
}

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
}
