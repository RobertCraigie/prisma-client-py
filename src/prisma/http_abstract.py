from abc import abstractmethod, ABC
from typing import (
    Union,
    Coroutine,
    Type,
    Dict,
    TypeVar,
    Generic,
    Optional,
    cast,
)

from httpx import Limits, Timeout

from ._types import Method
from .utils import _NoneType
from .errors import HTTPClientClosedError


Session = TypeVar('Session')
Response = TypeVar('Response')
ReturnType = TypeVar('ReturnType')
MaybeCoroutine = Union[Coroutine[object, object, ReturnType], ReturnType]

DEFAULT_CONFIG: Dict[str, object] = {
    'limits': Limits(max_connections=1000),
    'timeout': Timeout(30),
}


class AbstractHTTP(ABC, Generic[Session, Response]):
    session_kwargs: Dict[str, object]

    __slots__ = (
        '_session',
        'session_kwargs',
    )

    # NOTE: ParamSpec wouldn't be valid here:
    # https://github.com/microsoft/pyright/issues/2667
    def __init__(self, **kwargs: object) -> None:
        # NoneType = not used yet
        # None = closed
        # Session = open
        self._session: Optional[Union[Session, Type[_NoneType]]] = _NoneType
        self.session_kwargs = {
            **DEFAULT_CONFIG,
            **kwargs,
        }

    @abstractmethod
    def download(self, url: str, dest: str) -> MaybeCoroutine[None]:
        ...

    @abstractmethod
    def request(
        self,
        method: Method,
        url: str,
        **kwargs: object,
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

        # TODO: make this not strict, just open a new session
        if session is None:
            raise HTTPClientClosedError()

        return cast(Session, session)

    @session.setter
    def session(
        self, value: Optional[Session]
    ) -> None:  # pyright: ignore[reportPropertyTypeMismatch]
        self._session = value

    def should_close(self) -> bool:
        return self._session is not _NoneType and not self.closed

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'<HTTP closed={self.closed}>'


class AbstractResponse(ABC, Generic[Response]):
    original: Response

    __slots__ = ('original',)

    def __init__(self, original: Response) -> None:
        self.original = original

    @property
    @abstractmethod
    def status(self) -> int:
        ...

    @abstractmethod
    def json(self) -> MaybeCoroutine[object]:
        ...

    @abstractmethod
    def text(self) -> MaybeCoroutine[str]:
        ...

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'<Response wrapped={self.original} >'
