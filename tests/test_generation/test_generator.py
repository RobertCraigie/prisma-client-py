import sys
import subprocess
from typing import cast
from pathlib import Path
from typing_extensions import override

import pytest
from jinja2 import Environment, FileSystemLoader

from prisma import __version__
from prisma._compat import PYDANTIC_V2
from prisma.generator import (
    BASE_PACKAGE_DIR,
    Manifest,
    Generator,
    GenericGenerator,
    render_template,
    cleanup_templates,
)
from prisma.generator.utils import Faker, copy_tree

from .utils import assert_module_is_clean, assert_module_not_clean
from ..utils import Testdir


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


def test_erroneous_template_cleanup(testdir: Testdir) -> None:
    """Template runtime errors do not result in a partially generated module"""
    path = testdir.path / 'prisma'
    copy_tree(BASE_PACKAGE_DIR, path)

    assert_module_not_clean(path)

    template = '{{ undefined.foo }}'
    template_path = testdir.path / 'prisma' / 'generator' / 'templates' / 'template.py.jinja'
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

    assert exc.value.args[0] == 'Attempted to invoke a generator outside of Prisma generation'


def test_invalid_type_argument() -> None:
    """Non-BaseModel argument to GenericGenerator raises an error"""

    class MyGenerator(GenericGenerator[Path]):  # type: ignore
        @override
        def get_manifest(self) -> Manifest:  # pragma: no cover
            return super().get_manifest()  # type: ignore

        @override
        def generate(self, data: Path) -> None:  # pragma: no cover
            raise NotImplementedError()

    with pytest.raises(TypeError) as exc:
        MyGenerator().data_class  # noqa: B018

    assert 'pathlib.Path' in exc.value.args[0]
    assert 'pydantic.main.BaseModel' in exc.value.args[0]

    class MyGenerator2(GenericGenerator[Manifest]):
        @override
        def get_manifest(self) -> Manifest:  # pragma: no cover
            return super().get_manifest()  # type: ignore

        @override
        def generate(self, data: Manifest) -> None:  # pragma: no cover
            raise NotImplementedError()

    data_class = MyGenerator2().data_class
    assert data_class == Manifest


def test_generator_subclass_mismatch() -> None:
    """Attempting to subclass Generator instead of BaseGenerator raises an error"""
    with pytest.raises(TypeError) as exc:

        class MyGenerator(Generator):  # pyright: ignore[reportUnusedClass]
            ...

    message = exc.value.args[0]
    assert 'cannot be subclassed, maybe you meant' in message
    assert 'BaseGenerator' in message


def test_error_handling(testdir: Testdir) -> None:
    """Config validation errors are returned through JSONRPC without a stack trace"""
    with pytest.raises(subprocess.CalledProcessError) as exc:
        testdir.generate(options='partial_type_generator = "foo"')

    output = cast(bytes, exc.value.output).decode('utf-8').strip()
    if PYDANTIC_V2:
        line = output.splitlines()[-2]
        assert (
            line
            == "  Value error, Could not find a python file or module at foo [type=value_error, input_value='foo', input_type=str]"
        )
    else:
        assert output.endswith(
            '\nError: \n'
            '1 validation error for PythonData\n'
            'generator -> config -> partial_type_generator -> spec\n'
            '  Could not find a python file or module at foo (type=value_error)'
        )


def test_schema_path_same_path(testdir: Testdir) -> None:
    """Generating to the same directory does not cause any errors due to schema copying

    https://github.com/RobertCraigie/prisma-client-py/issues/513
    """
    proc = testdir.generate(output='.')
    assert proc.returncode == 0
    assert 'Generated Prisma Client Python' in proc.stdout.decode('utf-8')
