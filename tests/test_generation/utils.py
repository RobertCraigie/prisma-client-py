from typing import Iterator
from pathlib import Path

from prisma.generator.utils import resolve_template_path


def iter_templates_dir(path: Path) -> Iterator[Path]:
    templates = path / 'generator' / 'templates'
    assert templates.exists()

    for template in templates.iterdir():
        name = template.name

        if template.is_dir() or not name.endswith('.py.jinja') or name.startswith('_'):
            continue

        yield resolve_template_path(path, template.relative_to(templates))


def assert_module_is_clean(path: Path) -> None:
    for template in iter_templates_dir(path):
        assert not template.exists()


def assert_module_not_clean(path: Path) -> None:
    for template in iter_templates_dir(path):
        assert template.exists()
