from typing import Union
from pathlib import Path


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
