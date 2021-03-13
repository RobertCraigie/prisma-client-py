from abc import abstractmethod, ABC
from typing import Any, Union, Coroutine, TypeVar, Generic, Optional

from ._types import Method


Session = TypeVar('Session')
Response = TypeVar('Response')
ReturnType = TypeVar('ReturnType')
MaybeCoroutine = Union[Coroutine[Any, Any, ReturnType], ReturnType]


class AbstractHTTP(ABC, Generic[Session, Response]):
    def __init__(self) -> None:
        self.session = None  # type: Optional[Session]
        self.open()

    @abstractmethod
    def __del__(self) -> None:
        ...

    @abstractmethod
    def download(self, url: str, dest: str) -> MaybeCoroutine[None]:
        ...

    @abstractmethod
    def request(
        self, method: Method, url: str, **kwargs: Any
    ) -> MaybeCoroutine['AbstractResponse[Response]']:
        ...

    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self, session: Optional[Session] = None) -> MaybeCoroutine[None]:
        ...

    @property
    def closed(self) -> bool:
        return self.session is None

    @property
    @abstractmethod
    def library(self) -> str:
        ...

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'<HTTP library={self.library} closed={self.closed}>'


class AbstractResponse(ABC, Generic[Response]):
    def __init__(self, original: Response) -> None:
        self.original = original

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

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'<Response wrapped={self.original} >'
