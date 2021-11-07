import os
import shutil
from typing import Any, Union
from pathlib import Path

from ..utils import monkeypatch


def is_same_path(path: Path, other: Path) -> bool:
    return str(path.resolve()).strip() == str(other.resolve()).strip()


def resolve_template_path(rootdir: Path, name: Union[str, Path]) -> Path:
    return rootdir.joinpath(remove_suffix(name, '.jinja'))


def resolve_original_file(file: Path) -> Path:
    return file.parent.joinpath(file.name + '.original')


def remove_suffix(path: Union[str, Path], suf: str) -> str:
    """Remove a suffix from a string, if it exists."""
    # modified from https://stackoverflow.com/a/18723694
    if isinstance(path, Path):
        path = str(path)

    if suf and path.endswith(suf):
        return path[: -len(suf)]
    return path


def copy_tree(src: Path, dst: Path) -> None:
    """Recursively copy the contents of a directory from src to dst"""
    # we have to do this horrible monkeypatching as
    # shutil makes an arbitrary call to os.makedirs
    # which will fail if the directory already exists.
    # the dirs_exist_ok argument does exist but was only
    # added in python 3.8 so we cannot use that :(

    def _patched_makedirs(
        makedirs: Any, name: str, mode: int = 511, exist_ok: bool = True
    ) -> None:
        makedirs(name, mode, exist_ok=True)

    with monkeypatch(os, 'makedirs', _patched_makedirs):
        shutil.copytree(str(src), str(dst))
