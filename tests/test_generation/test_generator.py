import sys
import subprocess
from pathlib import Path
from typing import Iterator

import pytest
from jinja2 import Environment, FileSystemLoader
from prisma import __version__
from prisma.generator import (
    BASE_PACKAGE_DIR,
    Data,
    Manifest,
    Generator,
    GenericGenerator,
    render_template,
    cleanup_templates,
)
from prisma.generator.generator import OVERRIDING_TEMPLATES
from prisma.generator.utils import Faker, resolve_template_path, copy_tree

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
                assert 'template' not in content
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
                assert 'template' in content
            else:  # pragma: no cover
                assert False, f'Unhandled check for {template}'
        else:
            assert template.exists()


def test_repeated_rstrip_bug(tmp_path: Path) -> None:
    """Previously, rendering schema.prisma.jinja would have rendered the file
    to schema.prism instead of schema.prisma
    """
    env = Environment(loader=FileSystemLoader(str(tmp_path)))

    template = 'schema.prisma.jinja'
    tmp_path.joinpath(template).write_text('foo')
    render_template(tmp_path, template, dict(), env=env)

    assert tmp_path.joinpath('schema.prisma').read_text() == 'foo'


def test_template_cleanup(testdir: Testdir) -> None:
    """Cleaning up templates removes all rendered files"""
    path = testdir.path / 'prisma'
    assert not path.exists()
    copy_tree(BASE_PACKAGE_DIR, path)

    assert_module_not_clean(path)
    cleanup_templates(path)
    assert_module_is_clean(path)

    # ensure cleaning an already clean module doesn't change anything
    cleanup_templates(path)
    assert_module_is_clean(path)


def test_template_cleanup_original_files_not_replaced(testdir: Testdir) -> None:
    """Generating the client twice does not override template backups"""
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
    """Template runtime errors do not result in a partially generated module"""
    path = testdir.path / 'prisma'
    copy_tree(BASE_PACKAGE_DIR, path)

    assert_module_not_clean(path)

    template = '{{ undefined.foo }}'
    template_path = (
        testdir.path / 'prisma' / 'generator' / 'templates' / 'template.py.jinja'
    )
    template_path.write_text(template)

    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate()

    output = str(exc.value.output, sys.getdefaultencoding())
    assert template in output

    assert_module_is_clean(path)


def test_generation_version_number(testdir: Testdir) -> None:
    """Ensure the version number is shown when the client is generated"""
    stdout = testdir.generate().stdout.decode('utf-8')
    assert f'Generated Prisma Client Python (v{__version__})' in stdout


def test_faker() -> None:
    """Ensure Faker is re-playable"""
    iter1 = iter(Faker())
    iter2 = iter(Faker())
    first = [next(iter1) for _ in range(10)]
    second = [next(iter2) for _ in range(10)]
    assert first == second


def test_invoke_outside_generation() -> None:
    """Attempting to invoke a generator outside of Prisma generation errors"""
    with pytest.raises(RuntimeError) as exc:
        Generator.invoke()

    assert (
        exc.value.args[0]
        == 'Attempted to invoke a generator outside of Prisma generation'
    )


@pytest.mark.skipif(
    sys.version_info[:2] != (3, 6), reason='Test is only valid on python 3.6'
)
def test_data_class_required_py36() -> None:
    """Due to internal Generic workings, we cannot resolve generic arguments
    on python 3.6, our solution is that a `data_class` property must be required.
    """

    class MyGenerator(GenericGenerator[Data]):
        def get_manifest(self) -> Manifest:
            return super().get_manifest()

        def generate(self, data: Data) -> None:
            return super().generate(data)

    with pytest.raises(RuntimeError) as exc:
        MyGenerator().data_class

    assert 'data_class' in exc.value.args[0]


@pytest.mark.skipif(
    sys.version_info[:2] == (3, 6), reason='Test is not valid on python 3.6'
)
def test_invalid_type_argument() -> None:
    """Non-BaseModel argument to GenericGenerator raises an error"""

    class MyGenerator(GenericGenerator[Path]):  # type: ignore
        def get_manifest(self) -> Manifest:
            return super().get_manifest()

        def generate(self, data: Path) -> None:
            return super().generate(data)

    with pytest.raises(TypeError) as exc:
        MyGenerator().data_class

    assert 'pathlib.Path' in exc.value.args[0]
    assert 'pydantic.main.BaseModel' in exc.value.args[0]

    class MyGenerator2(GenericGenerator[Manifest]):
        def get_manifest(self) -> Manifest:
            return super().get_manifest()

        def generate(self, data: Manifest) -> None:
            return super().generate(data)

    data_class = MyGenerator2().data_class
    assert data_class == Manifest


def test_generator_subclass_mismatch() -> None:
    """Attempting to subclass Generator instead of BaseGenerator raises an error"""
    with pytest.raises(TypeError) as exc:

        class MyGenerator(Generator):  # type: ignore
            ...

    message = exc.value.args[0]
    assert 'cannot be subclassed, maybe you meant' in message
    assert 'BaseGenerator' in message
