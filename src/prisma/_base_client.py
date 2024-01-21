from __future__ import annotations

import logging
import warnings
from typing import Any, Generic, TypeVar
from datetime import timedelta
from typing_extensions import Self

from ._types import HttpConfig, TransactionId, DatasourceOverride
from .engine import BaseAbstractEngine
from .errors import ClientNotConnectedError, ClientNotRegisteredError
from ._registry import get_client

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


_EngineT = TypeVar('_EngineT', bound=BaseAbstractEngine)


class BasePrisma(Generic[_EngineT]):
    _log_queries: bool
    _datasource: DatasourceOverride | None
    _connect_timeout: int | timedelta
    _tx_id: TransactionId | None
    _http_config: HttpConfig
    _internal_engine: _EngineT | None
    _copied: bool

    __slots__ = (
        '_copied',
        '_tx_id',
        '_datasource',
        '_log_queries',
        '_http_config',
        '_connect_timeout',
        '_internal_engine',
    )

    def __init__(
        self,
        *,
        use_dotenv: bool,
        log_queries: bool,
        datasource: DatasourceOverride | None,
        connect_timeout: int | timedelta,
        http: HttpConfig | None,
    ) -> None:
        # NOTE: if you add any more properties here then you may also need to forward
        # them in the `_copy()` method.
        self._internal_engine = None
        self._log_queries = log_queries
        self._datasource = datasource

        if isinstance(connect_timeout, int):
            message = (
                'Passing an int as `connect_timeout` argument is deprecated '
                'and will be removed in the next major release. '
                'Use a `datetime.timedelta` instance instead.'
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            connect_timeout = timedelta(seconds=connect_timeout)

        self._connect_timeout = connect_timeout
        self._http_config: HttpConfig = http or {}
        self._tx_id: TransactionId | None = None
        self._copied: bool = False

        if use_dotenv:
            load_env()

    def is_registered(self) -> bool:
        """Returns True if this client instance is registered"""
        try:
            return get_client() is self
        except ClientNotRegisteredError:
            return False

    def is_connected(self) -> bool:
        """Returns True if the client is connected to the query engine, False otherwise."""
        return self._internal_engine is not None

    def __del__(self) -> None:
        # Note: as the transaction manager holds a reference to the original
        # client as well as the transaction client the original client cannot
        # be `free`d before the transaction is finished. So stopping the engine
        # here should be safe.
        if self._internal_engine is not None and not self._copied:
            log.debug('unclosed client - stopping engine')
            engine = self._internal_engine
            self._internal_engine = None
            engine.stop()

    @property
    def _engine(self) -> _EngineT:
        engine = self._internal_engine
        if engine is None:
            raise ClientNotConnectedError()
        return engine

    @_engine.setter
    def _engine(self, engine: _EngineT) -> None:
        self._internal_engine = engine

    def _copy(self) -> Self:
        """Return a new Prisma instance using the same engine process (if connected).

        This is only intended for private usage, there are no guarantees around this API.
        """
        new = self.__class__(
            use_dotenv=False,
            http=self._http_config,
            datasource=self._datasource,
            log_queries=self._log_queries,
            connect_timeout=self._connect_timeout,
        )
        new._copied = True

        if self._internal_engine is not None:
            new._engine = self._internal_engine

        return new
