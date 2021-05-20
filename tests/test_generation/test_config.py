import subprocess

import pytest

from ..utils import Testdir


def test_skip_plugins(testdir: Testdir) -> None:
    def plugin() -> None:  # mark: filedef
        raise RuntimeError('Plugin ran')

    def setup() -> None:  # mark: filedef
        # -*- coding: utf-8 -*-
        import setuptools  # type: ignore[import]

        setuptools.setup(
            name='prisma-plugin',
            version='0.0.1a',
            install_requires=[],
            python_requires='>=3',
            packages=['mod'],
            entry_points={
                'prisma': ['prisma-plugin = mod.plugin'],
            },
        )

    testdir.create_module(plugin)
    testdir.make_from_function(setup, name='setup.py')

    with testdir.install_module('prisma-plugin'):
        testdir.generate(options='skip_plugins = True')

        for options in ['', 'skip_plugins = False']:
            with pytest.raises(subprocess.CalledProcessError) as exc:
                testdir.generate(options=options)

            assert 'RuntimeError: Plugin ran' in str(exc.value.output)
