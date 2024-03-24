from __future__ import annotations

import logging
import warnings
from types import TracebackType
from typing import Any, Generic, TypeVar, overload
from pathlib import Path
from datetime import timedelta
from typing_extensions import Self, Literal

from pydantic import BaseModel

from ._types import Datasource, HttpConfig, PrismaMethod, MetricsFormat, TransactionId, DatasourceOverride
from .engine import (
    SyncQueryEngine,
    AsyncQueryEngine,
    BaseAbstractEngine,
    SyncAbstractEngine,
    AsyncAbstractEngine,
)
from .errors import ClientNotConnectedError, ClientNotRegisteredError
from ._compat import model_parse, removeprefix
from ._builder import QueryBuilder
from ._metrics import Metrics
from ._registry import get_client
from .generator.models import EngineType

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

    # from generation
    _schema_path: Path
    _prisma_models: set[str]
    _packaged_schema_path: Path
    _engine_type: EngineType
    _default_datasource_name: str
    _relational_field_mappings: dict[str, dict[str, str]]

    __slots__ = (
        '_copied',
        '_tx_id',
        '_datasource',
        '_log_queries',
        '_http_config',
        '_schema_path',
        '_engine_type',
        '_prisma_models',
        '_active_provider',
        '_connect_timeout',
        '_internal_engine',
        '_packaged_schema_path',
        '_default_datasource_name',
        '_relational_field_mappings',
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

    def _set_generated_properties(
        self,
        *,
        schema_path: Path,
        engine_type: EngineType,
        packaged_schema_path: Path,
        active_provider: str,
        prisma_models: set[str],
        relational_field_mappings: dict[str, dict[str, str]],
        default_datasource_name: str,
    ) -> None:
        """We pass through generated metadata using this method
        instead of the `__init__()` because that causes weirdness
        for our `_copy()` method as this base class has arguments
        that the subclasses do not.
        """
        self._schema_path = schema_path
        self._engine_type = engine_type
        self._prisma_models = prisma_models
        self._active_provider = active_provider
        self._packaged_schema_path = packaged_schema_path
        self._relational_field_mappings = relational_field_mappings
        self._default_datasource_name = default_datasource_name

    @property
    def _default_datasource(self) -> Datasource:
        raise NotImplementedError('`_default_datasource` should be implemented in a subclass')

    def is_registered(self) -> bool:
        """Returns True if this client instance is registered"""
        try:
            return get_client() is self
        except ClientNotRegisteredError:
            return False

    def is_transaction(self) -> bool:
        """Returns True if the client is wrapped within a transaction"""
        return self._tx_id is not None

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

    def _make_sqlite_datasource(self) -> DatasourceOverride:
        """Override the default SQLite path to protect against
        https://github.com/RobertCraigie/prisma-client-py/issues/409
        """
        return {
            'name': self._default_datasource['name'],
            'url': self._make_sqlite_url(self._default_datasource['url']),
        }

    def _make_sqlite_url(self, url: str, *, relative_to: Path | None = None) -> str:
        url_path = removeprefix(removeprefix(url, 'file:'), 'sqlite:')
        if url_path == url:
            return url

        if Path(url_path).is_absolute():
            return url

        if relative_to is None:
            relative_to = self._schema_path.parent

        return f'file:{relative_to.joinpath(url_path).resolve()}'

    def _prepare_connect_args(
        self,
        *,
        timeout: int | timedelta | UseClientDefault = USE_CLIENT_DEFAULT,
    ) -> tuple[timedelta, list[DatasourceOverride] | None]:
        """Returns (timeout, datasources) to be passed to `AbstractEngine.connect()`"""
        if isinstance(timeout, UseClientDefault):
            timeout = self._connect_timeout

        if isinstance(timeout, int):
            message = (
                'Passing an int as `timeout` argument is deprecated '
                'and will be removed in the next major release. '
                'Use a `datetime.timedelta` instance instead.'
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            timeout = timedelta(seconds=timeout)

        datasources: list[DatasourceOverride] | None = None
        if self._datasource is not None:
            ds = self._datasource.copy()
            ds.setdefault('name', self._default_datasource_name)
            datasources = [ds]
        elif self._active_provider == 'sqlite':
            # Override the default SQLite path to protect against
            # https://github.com/RobertCraigie/prisma-client-py/issues/409
            datasources = [self._make_sqlite_datasource()]

        return timeout, datasources

    def _make_query_builder(
        self,
        *,
        method: PrismaMethod,
        arguments: dict[str, Any],
        model: type[BaseModel] | None,
        root_selection: list[str] | None,
    ) -> QueryBuilder:
        return QueryBuilder(
            method=method,
            model=model,
            arguments=arguments,
            root_selection=root_selection,
            prisma_models=self._prisma_models,
            relational_field_mappings=self._relational_field_mappings,
        )


class SyncBasePrisma(BasePrisma[SyncAbstractEngine]):
    __slots__ = ()

    def connect(
        self,
        timeout: int | timedelta | UseClientDefault = USE_CLIENT_DEFAULT,
    ) -> None:
        """Connect to the Prisma query engine.

        It is required to call this before accessing data.
        """
        if self._internal_engine is None:
            self._internal_engine = self._create_engine(dml_path=self._packaged_schema_path)

        timeout, datasources = self._prepare_connect_args(timeout=timeout)

        self._internal_engine.connect(
            timeout=timeout,
            datasources=datasources,
        )

    def disconnect(self, timeout: float | timedelta | None = None) -> None:
        """Disconnect the Prisma query engine."""
        if self._internal_engine is not None:
            engine = self._internal_engine
            self._internal_engine = None

            if isinstance(timeout, (int, float)):
                message = (
                    'Passing a number as `timeout` argument is deprecated '
                    'and will be removed in the next major release. '
                    'Use a `datetime.timedelta` instead.'
                )
                warnings.warn(message, DeprecationWarning, stacklevel=2)
                timeout = timedelta(seconds=timeout)

            engine.close(timeout=timeout)
            engine.stop(timeout=timeout)

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.is_connected():
            self.disconnect()

    @overload
    def get_metrics(
        self,
        format: Literal['json'] = 'json',
        *,
        global_labels: dict[str, str] | None = None,
    ) -> Metrics:
        ...

    @overload
    def get_metrics(
        self,
        format: Literal['prometheus'],
        *,
        global_labels: dict[str, str] | None = None,
    ) -> str:
        ...

    def get_metrics(
        self,
        format: MetricsFormat = 'json',
        *,
        global_labels: dict[str, str] | None = None,
    ) -> str | Metrics:
        """Metrics give you a detailed insight into how the Prisma Client interacts with your database.

        You can retrieve metrics in either JSON or Prometheus formats.

        For more details see https://www.prisma.io/docs/concepts/components/prisma-client/metrics.
        """
        response = self._engine.metrics(format=format, global_labels=global_labels)
        if format == 'prometheus':
            # For the prometheus format we return the response as-is
            assert isinstance(response, str)
            return response

        return model_parse(Metrics, response)

    def _create_engine(self, dml_path: Path | None = None) -> SyncAbstractEngine:
        if self._engine_type == EngineType.binary:
            return SyncQueryEngine(
                dml_path=dml_path or self._packaged_schema_path,
                log_queries=self._log_queries,
                http_config=self._http_config,
            )

        raise NotImplementedError(f'Unsupported engine type: {self._engine_type}')

    @property
    def _engine_class(self) -> type[SyncAbstractEngine]:
        if self._engine_type == EngineType.binary:
            return SyncQueryEngine

        raise RuntimeError(f'Unhandled engine type: {self._engine_type}')

    # TODO: don't return Any
    def _execute(
        self,
        method: PrismaMethod,
        arguments: dict[str, Any],
        model: type[BaseModel] | None = None,
        root_selection: list[str] | None = None,
    ) -> Any:
        builder = self._make_query_builder(
            method=method, model=model, arguments=arguments, root_selection=root_selection
        )
        return self._engine.query(builder.build(), tx_id=self._tx_id)


class AsyncBasePrisma(BasePrisma[AsyncAbstractEngine]):
    __slots__ = ()

    async def connect(
        self,
        timeout: int | timedelta | UseClientDefault = USE_CLIENT_DEFAULT,
    ) -> None:
        """Connect to the Prisma query engine.

        It is required to call this before accessing data.
        """
        if self._internal_engine is None:
            self._internal_engine = self._create_engine(dml_path=self._packaged_schema_path)

        timeout, datasources = self._prepare_connect_args(timeout=timeout)

        await self._internal_engine.connect(
            timeout=timeout,
            datasources=datasources,
        )

    async def disconnect(self, timeout: float | timedelta | None = None) -> None:
        """Disconnect the Prisma query engine."""
        if self._internal_engine is not None:
            engine = self._internal_engine
            self._internal_engine = None

            if isinstance(timeout, (int, float)):
                message = (
                    'Passing a number as `timeout` argument is deprecated '
                    'and will be removed in the next major release. '
                    'Use a `datetime.timedelta` instead.'
                )
                warnings.warn(message, DeprecationWarning, stacklevel=2)
                timeout = timedelta(seconds=timeout)

            await engine.aclose(timeout=timeout)
            engine.stop(timeout=timeout)

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.is_connected():
            await self.disconnect()

    @overload
    async def get_metrics(
        self,
        format: Literal['json'] = 'json',
        *,
        global_labels: dict[str, str] | None = None,
    ) -> Metrics:
        ...

    @overload
    async def get_metrics(
        self,
        format: Literal['prometheus'],
        *,
        global_labels: dict[str, str] | None = None,
    ) -> str:
        ...

    async def get_metrics(
        self,
        format: MetricsFormat = 'json',
        *,
        global_labels: dict[str, str] | None = None,
    ) -> str | Metrics:
        """Metrics give you a detailed insight into how the Prisma Client interacts with your database.

        You can retrieve metrics in either JSON or Prometheus formats.

        For more details see https://www.prisma.io/docs/concepts/components/prisma-client/metrics.
        """
        response = await self._engine.metrics(format=format, global_labels=global_labels)
        if format == 'prometheus':
            # For the prometheus format we return the response as-is
            assert isinstance(response, str)
            return response

        return model_parse(Metrics, response)

    def _create_engine(self, dml_path: Path | None = None) -> AsyncAbstractEngine:
        if self._engine_type == EngineType.binary:
            return AsyncQueryEngine(
                dml_path=dml_path or self._packaged_schema_path,
                log_queries=self._log_queries,
                http_config=self._http_config,
            )

        raise NotImplementedError(f'Unsupported engine type: {self._engine_type}')

    @property
    def _engine_class(self) -> type[AsyncAbstractEngine]:
        if self._engine_type == EngineType.binary:
            return AsyncQueryEngine

        raise RuntimeError(f'Unhandled engine type: {self._engine_type}')

    # TODO: don't return Any
    async def _execute(
        self,
        *,
        method: PrismaMethod,
        arguments: dict[str, Any],
        model: type[BaseModel] | None = None,
        root_selection: list[str] | None = None,
    ) -> Any:
        builder = self._make_query_builder(
            method=method, model=model, arguments=arguments, root_selection=root_selection
        )
        return await self._engine.query(builder.build(), tx_id=self._tx_id)
