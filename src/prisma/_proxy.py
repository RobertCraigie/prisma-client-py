from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar('T')


# TODO: ensure things like __name__, __dir__ are proxied correctly
class LazyProxy(Generic[T], ABC):
    def __init__(self) -> None:
        self.__proxied: T | None = None

    def __getattr__(self, attr: str) -> object:
        return getattr(self.__get_proxied(), attr)

    def __repr__(self) -> str:
        return repr(self.__get_proxied())

    def __str__(self) -> str:
        return str(self.__get_proxied())

    def __get_proxied(self) -> T:
        proxied = self.__proxied
        if proxied is not None:
            return proxied

        self.__proxied = proxied = self.__load__()
        return proxied

    @abstractmethod
    def __load__(self) -> T:
        ...
