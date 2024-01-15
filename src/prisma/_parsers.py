from __future__ import annotations

from typing import Any, Callable, TypeVar

from ._helpers import is_list


_T = TypeVar('_T')


def allow_none(parser: Callable[[Any], _T]) -> Callable[[Any], _T | None]:
    """Wrap the given parser function to allow passing in None values."""

    def wrapped(value: Any) -> _T | None:
        if value is None:
            return None

        return parser(value)

    return wrapped


def as_list(parser: Callable[[Any], _T]) -> Callable[[Any], list[_T]]:
    """Wrap the given parser function to accept a list and invoke it for each entry"""

    def wrapped(value: Any) -> list[_T]:
        if not is_list(value):
            raise TypeError(
                f'Expected value to be a list but got {type(value)}'
            )

        return [parser(entry) for entry in value]

    return wrapped
