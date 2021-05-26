# All string functions are heavily inspired by https://github.com/nficano/humps
import re
from typing import Union
from pathlib import Path


ACRONYM_RE = re.compile(r"([A-Z]+)(?=[A-Z][a-z])")
PASCAL_RE = re.compile(r"([^\-_\s]+)")
SPLIT_RE = re.compile(r"([\-_\s]*[A-Z0-9]+[^A-Z\-_\s]+[\-_\s]*)")
UNDERSCORE_RE = re.compile(r"([^\-_\s])[\-_\s]+([^\-_\s])")


def camelize(string: str) -> str:
    """Convert a string to camelCase."""
    if string.isupper():
        return string

    return ''.join(
        [
            string[0].lower() if not string[:2].isupper() else string[0],
            UNDERSCORE_RE.sub(lambda m: m.group(1) + m.group(2).upper(), string[1:]),
        ]
    )


def pascalize(string: str) -> str:
    """Convert a string to PascalCase."""
    if string.isupper():
        return string

    string = camelize(
        PASCAL_RE.sub(lambda m: m.group(1)[0].upper() + m.group(1)[1:], string),
    )
    return string[0].upper() + string[1:]


def decamelize(string: str) -> str:
    """Convert a string to snake_case"""
    if string.isupper():
        return string

    return '_'.join(s for s in SPLIT_RE.split(_fix_abbrevations(string)) if s).lower()


def _fix_abbrevations(string: str) -> str:
    """Ensure "APIReponse" returns "api_reponse"."""
    return ACRONYM_RE.sub(lambda m: m.group(0).title(), string)


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
