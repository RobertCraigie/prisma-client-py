from __future__ import annotations

import logging
import warnings
from types import TracebackType
from typing import TYPE_CHECKING, Generic, TypeVar
from datetime import timedelta

from ._types import TransactionId
from .errors import TransactionNotStartedError
from ._builder import dumps

if TYPE_CHECKING:
    from ._base_client import SyncBasePrisma, AsyncBasePrisma

log: logging.Logger = logging.getLogger(__name__)


_SyncPrismaT = TypeVar('_SyncPrismaT', bound='SyncBasePrisma')
_AsyncPrismaT = TypeVar('_AsyncPrismaT', bound='AsyncBasePrisma')


class AsyncTransactionManager(Generic[_AsyncPrismaT]):
    """Context manager for wrapping a Prisma instance within a transaction.

    This should never be created manually, instead it should be used
    through the Prisma.tx() method.
    """

    def __init__(
        self,
        *,
        client: _AsyncPrismaT,
        max_wait: int | timedelta,
        timeout: int | timedelta,
    ) -> None:
        self.__client = client

        if isinstance(max_wait, int):
            message = (
                'Passing an int as `max_wait` argument is deprecated '
                'and will be removed in the next major release. '
                'Use a `datetime.timedelta` instance instead.'
            )
            warnings.warn(message, DeprecationWarning, stacklevel=3)
            max_wait = timedelta(milliseconds=max_wait)

        self._max_wait = max_wait

        if isinstance(timeout, int):
            message = (
                'Passing an int as `timeout` argument is deprecated '
                'and will be removed in the next major release. '
                'Use a `datetime.timedelta` instance instead.'
            )
            warnings.warn(message, DeprecationWarning, stacklevel=3)
            timeout = timedelta(milliseconds=timeout)

        self._timeout = timeout

        self._tx_id: TransactionId | None = None

    async def start(self, *, _from_context: bool = False) -> _AsyncPrismaT:
        """Start the transaction and return the wrapped Prisma instance"""
        if self.__client.is_transaction():
            # if we were called from the context manager then the stacklevel
            # needs to be one higher to warn on the actual offending code
            warnings.warn(
                'The current client is already in a transaction. This can lead to surprising behaviour.',
                UserWarning,
                stacklevel=3 if _from_context else 2,
            )

        tx_id = await self.__client._engine.start_transaction(
            content=dumps(
                {
                    'timeout': int(self._timeout.total_seconds() * 1000),
                    'max_wait': int(self._max_wait.total_seconds() * 1000),
                }
            ),
        )
        self._tx_id = tx_id
        client = self.__client._copy()
        client._tx_id = tx_id
        return client

    async def commit(self) -> None:
        """Commit the transaction to the database, this transaction will no longer be usable"""
        if self._tx_id is None:
            raise TransactionNotStartedError()

        await self.__client._engine.commit_transaction(self._tx_id)

    async def rollback(self) -> None:
        """Do not commit the changes to the database, this transaction will no longer be usable"""
        if self._tx_id is None:
            raise TransactionNotStartedError()

        await self.__client._engine.rollback_transaction(self._tx_id)

    async def __aenter__(self) -> _AsyncPrismaT:
        return await self.start(_from_context=True)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc is None:
            log.debug('Transaction exited with no exception - commiting')
            await self.commit()
            return

        log.debug('Transaction exited with exc type: %s - rolling back', exc_type)

        try:
            await self.rollback()
        except Exception as exc:
            log.warning(
                'Encountered exc `%s` while rolling back a transaction. Ignoring and raising original exception', exc
            )


class SyncTransactionManager(Generic[_SyncPrismaT]):
    """Context manager for wrapping a Prisma instance within a transaction.

    This should never be created manually, instead it should be used
    through the Prisma.tx() method.
    """

    def __init__(
        self,
        *,
        client: _SyncPrismaT,
        max_wait: int | timedelta,
        timeout: int | timedelta,
    ) -> None:
        self.__client = client

        if isinstance(max_wait, int):
            message = (
                'Passing an int as `max_wait` argument is deprecated '
                'and will be removed in the next major release. '
                'Use a `datetime.timedelta` instance instead.'
            )
            warnings.warn(message, DeprecationWarning, stacklevel=3)
            max_wait = timedelta(milliseconds=max_wait)

        self._max_wait = max_wait

        if isinstance(timeout, int):
            message = (
                'Passing an int as `timeout` argument is deprecated '
                'and will be removed in the next major release. '
                'Use a `datetime.timedelta` instance instead.'
            )
            warnings.warn(message, DeprecationWarning, stacklevel=3)
            timeout = timedelta(milliseconds=timeout)

        self._timeout = timeout

        self._tx_id: TransactionId | None = None

    def start(self, *, _from_context: bool = False) -> _SyncPrismaT:
        """Start the transaction and return the wrapped Prisma instance"""
        if self.__client.is_transaction():
            # if we were called from the context manager then the stacklevel
            # needs to be one higher to warn on the actual offending code
            warnings.warn(
                'The current client is already in a transaction. This can lead to surprising behaviour.',
                UserWarning,
                stacklevel=3 if _from_context else 2,
            )

        tx_id = self.__client._engine.start_transaction(
            content=dumps(
                {
                    'timeout': int(self._timeout.total_seconds() * 1000),
                    'max_wait': int(self._max_wait.total_seconds() * 1000),
                }
            ),
        )
        self._tx_id = tx_id
        client = self.__client._copy()
        client._tx_id = tx_id
        return client

    def commit(self) -> None:
        """Commit the transaction to the database, this transaction will no longer be usable"""
        if self._tx_id is None:
            raise TransactionNotStartedError()

        self.__client._engine.commit_transaction(self._tx_id)

    def rollback(self) -> None:
        """Do not commit the changes to the database, this transaction will no longer be usable"""
        if self._tx_id is None:
            raise TransactionNotStartedError()

        self.__client._engine.rollback_transaction(self._tx_id)

    def __enter__(self) -> _SyncPrismaT:
        return self.start(_from_context=True)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc is None:
            log.debug('Transaction exited with no exception - commiting')
            self.commit()
            return

        log.debug('Transaction exited with exc type: %s - rolling back', exc_type)

        try:
            self.rollback()
        except Exception as exc:
            log.warning(
                'Encountered exc `%s` while rolling back a transaction. Ignoring and raising original exception', exc
            )
