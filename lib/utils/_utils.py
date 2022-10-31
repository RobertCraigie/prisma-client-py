from typing import TypeVar


T = TypeVar('T')


def flatten(arr: list[list[T]]) -> list[T]:
    return [item for sublist in arr for item in sublist]
