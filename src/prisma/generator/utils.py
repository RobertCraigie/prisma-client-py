from __future__ import annotations

import os
import re
import shutil
from typing import TYPE_CHECKING, Any, Dict, List, Union, TypeVar, Iterator
from pathlib import Path
from textwrap import dedent

from ..utils import monkeypatch

if TYPE_CHECKING:
    from .models import Field, Model


T = TypeVar('T')

# we have to use a mapping outside of the `Sampler` class
# to avoid https://github.com/RobertCraigie/prisma-client-py/issues/402
SAMPLER_ITER_MAPPING: 'Dict[str, Iterator[Field]]' = {}


class Faker:
    """Pseudo-random re-playable data.

    Seeds are generated using a linear congruential generator, inspired by:
    https://stackoverflow.com/a/9024521/13923613
    """

    def __init__(self, seed: int = 1) -> None:
        self._state = seed

    def __iter__(self) -> 'Faker':
        return self

    def __next__(self) -> int:
        self._state = state = (self._state * 1103515245 + 12345) & 0x7FFFFFFF
        return state

    def string(self) -> str:
        return ''.join([chr(97 + int(n)) for n in str(self.integer())])

    def boolean(self) -> bool:
        return next(self) % 2 == 0

    def integer(self) -> int:
        return next(self)

    @classmethod
    def from_list(cls, values: List[T]) -> T:
        # TODO: actual implementation
        assert values, 'Expected non-empty list'
        return values[0]


class Sampler:
    model: 'Model'

    def __init__(self, model: 'Model') -> None:
        self.model = model
        SAMPLER_ITER_MAPPING[model.name] = model.scalar_fields

    def get_field(self) -> 'Field':
        mapping = SAMPLER_ITER_MAPPING

        try:
            field = next(mapping[self.model.name])
        except StopIteration:
            mapping[self.model.name] = field_iter = self.model.scalar_fields
            field = next(field_iter)

        return field


def is_same_path(path: Path, other: Path) -> bool:
    return str(path.resolve()).strip() == str(other.resolve()).strip()


def resolve_template_path(rootdir: Path, name: Union[str, Path]) -> Path:
    return rootdir.joinpath(remove_suffix(name, '.jinja'))


def remove_suffix(path: Union[str, Path], suf: str) -> str:
    """Remove a suffix from a string, if it exists."""
    # modified from https://stackoverflow.com/a/18723694
    if isinstance(path, Path):
        path = str(path)

    if suf and path.endswith(suf):
        return path[: -len(suf)]
    return path


def copy_tree(src: Path, dst: Path) -> None:
    """Recursively copy the contents of a directory from src to dst.

    This function will ignore certain compiled / cache files for convenience:
    - *.pyc
    - __pycache__
    """
    # we have to do this horrible monkeypatching as
    # shutil makes an arbitrary call to os.makedirs
    # which will fail if the directory already exists.
    # the dirs_exist_ok argument does exist but was only
    # added in python 3.8 so we cannot use that :(

    def _patched_makedirs(
        makedirs: Any,
        name: str,
        mode: int = 511,
        exist_ok: bool = True,  # noqa: ARG001
    ) -> None:
        makedirs(name, mode, exist_ok=True)

    with monkeypatch(os, 'makedirs', _patched_makedirs):
        shutil.copytree(
            str(src),
            str(dst),
            ignore=shutil.ignore_patterns('*.pyc', '__pycache__'),
        )


def clean_multiline(string: str) -> str:
    string = string.lstrip('\n')
    assert string, 'Expected non-empty string'
    lines = string.splitlines()
    return '\n'.join([dedent(lines[0]), *lines[1:]])


# https://github.com/nficano/humps/blob/master/humps/main.py

ACRONYM_RE = re.compile(r'([A-Z\d]+)(?=[A-Z\d]|$)')
PASCAL_RE = re.compile(r'([^\-_]+)')
SPLIT_RE = re.compile(r'([\-_]*[A-Z][^A-Z]*[\-_]*)')
UNDERSCORE_RE = re.compile(r'(?<=[^\-_])[\-_]+[^\-_]')


def to_snake_case(input_str: str) -> str:
    if to_camel_case(input_str) == input_str or to_pascal_case(input_str) == input_str:  # if camel case or pascal case
        input_str = ACRONYM_RE.sub(lambda m: m.group(0).title(), input_str)
        input_str = '_'.join(s for s in SPLIT_RE.split(input_str) if s)
        return input_str.lower()
    else:
        input_str = re.sub(r'[^a-zA-Z0-9]', '_', input_str)
        input_str = input_str.lower().strip('_')

        return input_str


def to_camel_case(input_str: str) -> str:
    if len(input_str) != 0 and not input_str[:2].isupper():
        input_str = input_str[0].lower() + input_str[1:]
    return UNDERSCORE_RE.sub(lambda m: m.group(0)[-1].upper(), input_str)


def to_pascal_case(input_str: str) -> str:
    def _replace_fn(match: re.Match[str]) -> str:
        return match.group(1)[0].upper() + match.group(1)[1:]

    input_str = to_camel_case(PASCAL_RE.sub(_replace_fn, input_str))
    return input_str[0].upper() + input_str[1:] if len(input_str) != 0 else input_str


def to_constant_case(input_str: str) -> str:
    """Converts to snake case + uppercase, examples:

    foo_bar -> FOO_BAR
    fooBar -> FOO_BAR
    """
    return to_snake_case(input_str).upper()
