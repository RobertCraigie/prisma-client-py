from abc import abstractmethod, ABC
from typing import Any, Union, Coroutine, Type, TypeVar, Generic, Optional, cast

from ._types import Method
from .utils import _NoneType
from .errors import HTTPClientClosedError


Session = TypeVar('Session')
Response = TypeVar('Response')
ReturnType = TypeVar('ReturnType')
MaybeCoroutine = Union[Coroutine[Any, Any, ReturnType], ReturnType]


class AbstractHTTP(ABC, Generic[Session, Response]):
    def __init__(self) -> None:
        # NoneType = not used yet
        # None = closed
        # Session = open
        self._session = _NoneType  # type: Optional[Union[Session, Type[_NoneType]]]

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
    def close(self) -> MaybeCoroutine[None]:
        ...

    @property
    def closed(self) -> bool:
        return self._session is None

    @property
    def session(self) -> Session:
        session = self._session
        if session is _NoneType:
            self.open()
            return cast(Session, self._session)

        if session is None:
            raise HTTPClientClosedError()

        return cast(Session, session)

    @session.setter
    def session(
        self, value: Optional[Session]
    ) -> None:  # pyright: reportPropertyTypeMismatch=false
        self._session = value

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'<HTTP closed={self.closed}>'


class AbstractResponse(ABC, Generic[Response]):
    original: Response

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
