from abc import abstractmethod, ABC
from typing import Any, Union, Coroutine, TypeVar

from ._types import Method


ReturnType = TypeVar('ReturnType')
MaybeCoroutine = Union[Coroutine[Any, Any, ReturnType], ReturnType]


class AbstractHTTP(ABC):
    @abstractmethod
    def __del__(self) -> None:
        ...

    @abstractmethod
    def download(self, url: str, dest: str) -> MaybeCoroutine[None]:
        ...

    @abstractmethod
    def request(
        self, method: Method, url: str, **kwargs: Any
    ) -> MaybeCoroutine['AbstractResponse']:
        ...

    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self) -> MaybeCoroutine[None]:
        ...

    @property
    @abstractmethod
    def closed(self) -> bool:
        ...

    @property
    @abstractmethod
    def library(self) -> str:
        ...


class AbstractResponse(ABC):
    @property
    @abstractmethod
    def status(self) -> int:
        ...

    @abstractmethod
    def json(self) -> MaybeCoroutine[Any]:
        ...

    @abstractmethod
    def text(self) -> MaybeCoroutine[Any]:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...
