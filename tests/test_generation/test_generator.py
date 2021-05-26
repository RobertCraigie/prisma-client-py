import subprocess
from pathlib import Path
from typing import Iterator
from distutils.dir_util import copy_tree

import pytest
from jinja2 import Environment, FileSystemLoader
from prisma.generator import BASE_PACKAGE_DIR, render_template, cleanup_templates
from prisma.generator.generator import OVERRIDING_TEMPLATES
from prisma.generator.utils import resolve_template_path

from ..utils import Testdir


def iter_templates_dir(path: Path) -> Iterator[Path]:
    templates = path / 'generator' / 'templates'
    assert templates.exists()

    for template in templates.iterdir():
        name = template.name

        if template.is_dir() or not name.endswith('.py.jinja') or name.startswith('_'):
            continue

        yield resolve_template_path(path, template.relative_to(templates))


def is_overrided_file(file: Path) -> bool:
    # NOTE: this will not work correctly if an overriding template
    # contains a path separator
    return file.name + '.jinja' in OVERRIDING_TEMPLATES


def assert_module_is_clean(path: Path) -> None:
    for template in iter_templates_dir(path):
        if is_overrided_file(template):
            if template.name == 'http.py':
                content = template.read_text()

                # basic check to ensure that the original file has been reinstated
                assert 'aiohttp' in content
                assert 'requests' in content
            else:  # pragma: no cover
                assert False, f'Unhandled check for {template}'
        else:
            assert not template.exists()


def assert_module_not_clean(path: Path) -> None:
    for template in iter_templates_dir(path):
        if is_overrided_file(template):
            if template.name == 'http.py':
                content = template.read_text()

                # basic check to ensure that the original file has been replaced
                assert 'aiohttp' in content
                assert 'requests' not in content
            else:  # pragma: no cover
                assert False, f'Unhandled check for {template}'
        else:
            assert template.exists()


def test_repeated_rstrip_bug(tmp_path: Path) -> None:
    env = Environment(loader=FileSystemLoader(str(tmp_path)))

    template = 'schema.prisma.jinja'
    tmp_path.joinpath(template).write_text('foo')
    render_template(tmp_path, template, dict(), env=env)

    assert tmp_path.joinpath('schema.prisma').read_text() == 'foo'


def test_template_cleanup(testdir: Testdir) -> None:
    path = testdir.path / 'prisma'
    assert not path.exists()
    copy_tree(str(BASE_PACKAGE_DIR), str(path))

    assert_module_not_clean(path)
    cleanup_templates(path)
    assert_module_is_clean(path)

    # ensure cleaning an already clean module doesn't change anything
    cleanup_templates(path)
    assert_module_is_clean(path)


def test_template_cleanup_original_files_not_replaced(testdir: Testdir) -> None:
    path = testdir.path / 'prisma'
    assert not path.exists()

    # generate twice to ensure that originals of overriding templates
    # are not replaced
    testdir.generate()
    testdir.generate()

    assert_module_not_clean(path)
    cleanup_templates(path)
    assert_module_is_clean(path)


def test_erroneous_template_cleanup(testdir: Testdir) -> None:
    path = testdir.path / 'prisma'
    copy_tree(str(BASE_PACKAGE_DIR), str(path))

    assert_module_not_clean(path)

    template = '{{ undefined.foo }}'
    template_path = (
        testdir.path / 'prisma' / 'generator' / 'templates' / 'template.py.jinja'
    )
    template_path.write_text(template)

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate()

    output = str(exc.value.output, 'utf-8')
    assert template in output

    assert_module_is_clean(path)
