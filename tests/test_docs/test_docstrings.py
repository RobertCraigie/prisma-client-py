import re
import inspect
from typing import Any

import pytest

from prisma.actions import PostActions

METHODS = [member for name, member in inspect.getmembers(PostActions) if not name.startswith('_')]


@pytest.mark.parametrize('method', METHODS)
def test_headings(method: Any) -> None:
    """Ensure the Example, Parameters, Raises and Returns headings are present"""
    doc = inspect.getdoc(method)
    print(doc)
    assert doc is not None
    assert 'Raises\n------' in doc
    assert 'Example\n-------' in doc
    assert 'Returns\n-------' in doc
    assert 'Parameters\n----------' in doc
    assert 'prisma.errors.PrismaError' in doc


@pytest.mark.parametrize('method', METHODS)
def test_completeness(method: Any) -> None:
    """Ensure there aren't any incomplete docstrings"""
    doc = inspect.getdoc(method)
    print(doc)
    assert doc is not None

    for name, param in inspect.signature(method).parameters.items():
        if name == 'self':
            continue

        if param.kind == param.VAR_POSITIONAL:
            qualified = f'\\*{name}'
        else:
            qualified = name

        match = re.search(
            r'Parameters\n----------((.|\n)*)^{0}$((.|\n)*)Returns'.format(qualified),
            doc,
            re.MULTILINE,
        )
        assert match is not None, f'Missing documentation for parameter: {qualified}'

    assert 'TODO' not in doc
    assert method.__name__ in doc
