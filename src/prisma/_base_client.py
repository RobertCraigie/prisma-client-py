from __future__ import annotations

import logging
from typing import Any

log: logging.Logger = logging.getLogger(__name__)


class UseClientDefault:
    """For certain parameters such as `timeout=...` we can make our intent more clear
    by typing the parameter with this class rather than using None, for example:

    ```py
    def connect(timeout: Union[int, timedelta, UseClientDefault] = UseClientDefault()) -> None:
        ...
    ```

    relays the intention more clearly than:

    ```py
    def connect(timeout: Union[int, timedelta, None] = None) -> None:
        ...
    ```

    This solution also allows us to indicate an "unset" state that is uniquely distinct
    from `None` which may be useful in the future.
    """


USE_CLIENT_DEFAULT = UseClientDefault()


def load_env(*, override: bool = False, **kwargs: Any) -> None:
    """Load environemntal variables from dotenv files

    Loads from the following files relative to the current
    working directory:

    - .env
    - prisma/.env
    """
    from dotenv import load_dotenv

    load_dotenv('.env', override=override, **kwargs)
    load_dotenv('prisma/.env', override=override, **kwargs)
