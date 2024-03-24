from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, overload
from datetime import timedelta
from typing_extensions import Literal

from .._types import TransactionId
from .._compat import get_running_loop
from .._constants import DEFAULT_CONNECT_TIMEOUT

if TYPE_CHECKING:
    from ..types import MetricsFormat, DatasourceOverride  # noqa: TID251


__all__ = (
    'SyncAbstractEngine',
    'AsyncAbstractEngine',
)


class BaseAbstractEngine(ABC):
    dml: str

    def stop(self, *, timeout: timedelta | None = None) -> None:
        """Wrapper for synchronously calling close() and aclose()"""
        self.close(timeout=timeout)
        try:
            loop = get_running_loop()
        except RuntimeError:
            # no event loop in the current thread, we cannot cleanup asynchronously
            return
        else:
            if not loop.is_closed():
                loop.create_task(self.aclose(timeout=timeout))

    @abstractmethod
    def close(self, *, timeout: timedelta | None = None) -> None:
        """Synchronous method for closing the engine, useful if the underlying engine uses a subprocess"""
        ...

    # TODO(#871): don't include for the sync client
    @abstractmethod
    async def aclose(self, *, timeout: timedelta | None = None) -> None:
        """Asynchronous method for closing the engine, only used if an asynchronous client is generated"""
        ...


class SyncAbstractEngine(BaseAbstractEngine):
    @abstractmethod
    def connect(
        self,
        timeout: timedelta = DEFAULT_CONNECT_TIMEOUT,
        datasources: list[DatasourceOverride] | None = None,
    ) -> None:
        """Connect to the engine"""
        ...

    @abstractmethod
    def query(self, content: str, *, tx_id: TransactionId | None) -> Any:
        """Execute a GraphQL query.

        This method expects a JSON object matching this structure:

        {
            'variables': {},
            'operation_name': str,
            'query': str,
        }
        """
        ...

    @abstractmethod
    def start_transaction(self, *, content: str) -> TransactionId:
        """Start an interactive transaction, returns the transaction ID that can be used to perform subsequent operations"""
        ...

    @abstractmethod
    def commit_transaction(self, tx_id: TransactionId) -> None:
        """Commit an interactive transaction, the given transaction will no longer be usable"""
        ...

    @abstractmethod
    def rollback_transaction(self, tx_id: TransactionId) -> None:
        """Rollback an interactive transaction, the given transaction will no longer be usable"""
        ...

    @overload
    @abstractmethod
    def metrics(
        self,
        *,
        format: Literal['json'],
        global_labels: dict[str, str] | None,
    ) -> dict[str, Any]: ...

    @overload
    @abstractmethod
    def metrics(
        self,
        *,
        format: Literal['prometheus'],
        global_labels: dict[str, str] | None,
    ) -> str: ...

    @abstractmethod
    def metrics(
        self,
        *,
        format: MetricsFormat,
        global_labels: dict[str, str] | None,
    ) -> str | dict[str, Any]: ...


class AsyncAbstractEngine(BaseAbstractEngine):
    @abstractmethod
    async def connect(
        self,
        timeout: timedelta = DEFAULT_CONNECT_TIMEOUT,
        datasources: list[DatasourceOverride] | None = None,
    ) -> None:
        """Connect to the engine"""
        ...

    @abstractmethod
    async def query(self, content: str, *, tx_id: TransactionId | None) -> Any:
        """Execute a GraphQL query.

        This method expects a JSON object matching this structure:

        {
            'variables': {},
            'operation_name': str,
            'query': str,
        }
        """
        ...

    @abstractmethod
    async def start_transaction(self, *, content: str) -> TransactionId:
        """Start an interactive transaction, returns the transaction ID that can be used to perform subsequent operations"""
        ...

    @abstractmethod
    async def commit_transaction(self, tx_id: TransactionId) -> None:
        """Commit an interactive transaction, the given transaction will no longer be usable"""
        ...

    @abstractmethod
    async def rollback_transaction(self, tx_id: TransactionId) -> None:
        """Rollback an interactive transaction, the given transaction will no longer be usable"""
        ...

    @overload
    @abstractmethod
    async def metrics(
        self,
        *,
        format: Literal['json'],
        global_labels: dict[str, str] | None,
    ) -> dict[str, Any]: ...

    @overload
    @abstractmethod
    async def metrics(
        self,
        *,
        format: Literal['prometheus'],
        global_labels: dict[str, str] | None,
    ) -> str: ...

    @abstractmethod
    async def metrics(
        self,
        *,
        format: MetricsFormat,
        global_labels: dict[str, str] | None,
    ) -> str | dict[str, Any]: ...
