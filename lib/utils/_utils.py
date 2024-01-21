from __future__ import annotations

from typing import TypeVar
from pathlib import Path

T = TypeVar('T')


def flatten(arr: list[list[T]]) -> list[T]:
    return [item for sublist in arr for item in sublist]


def escape_path(path: str | Path) -> str:
    if isinstance(path, Path):  # pragma: no branch
        path = str(path.absolute())

    return path.replace('\\', '\\\\')


def maybe_decode(data: str | bytes) -> str:
    """Helper for decoding `bytes`.

    - Given a `bytes` object, return it decoded using utf8.
    - Given a `str` object, return it as is.
    """
    if isinstance(data, bytes):
        return data.decode('utf8')
    return data
