import os
import shutil
import subprocess
from typing import cast
from pathlib import Path

import pytest
from prisma.cli import _node as node
from prisma._config import Config
from prisma._compat import nodejs

from ..utils import set_config


# TODO: test npm usage too


THIS_DIR = Path(__file__).parent


def assert_can_run_js(strategy: node.Node) -> None:
    proc = strategy.run(
        str(THIS_DIR.joinpath('test.js')),
        stdout=subprocess.PIPE,
    )
    output = proc.stdout.decode('utf-8')
    assert output == 'Hello world!\n'


def test_resolve_bad_target() -> None:
    """resolve() raises a helpful error message when given an unknown target"""
    with pytest.raises(
        node.UnknownTargetError,
        match='Unknown target: foo; Valid choices are: node, npm',
    ):
        node.resolve(cast(node.Target, 'foo'))


@pytest.mark.skipif(nodejs is None, reason='nodejs-bin is not installed')
def test_nodejs_bin() -> None:
    """When `nodejs-bin` is installed, it is resolved to and can be successfully used"""
    with set_config(
        Config.parse(
            use_nodejs_bin=True,
            use_global_node=False,
        )
    ):
        strategy = node.resolve('node')
        assert strategy.resolver == 'nodejs-bin'
        assert_can_run_js(strategy)


@pytest.mark.skipif(
    shutil.which('node') is None,
    reason='Node is not installed globally',
)
def test_resolves_binary_node() -> None:
    """When `node` is installed globally, it is resolved to and can be successfully used"""
    with set_config(
        Config.parse(
            use_nodejs_bin=False,
            use_global_node=True,
        )
    ):
        strategy = node.resolve('node')
        assert strategy.resolver == 'global'
        assert_can_run_js(strategy)

    with set_config(
        Config.parse(
            use_nodejs_bin=False,
            use_global_node=False,
        )
    ):
        strategy = node.resolve('node')
        assert strategy.resolver == 'nodeenv'
        assert_can_run_js(strategy)


def test_nodeenv() -> None:
    """When `nodejs-bin` and global `node` is not installed / configured to use, `nodeenv` is resolved to and can be successfully used"""
    with set_config(
        Config.parse(
            use_nodejs_bin=False,
            use_global_node=False,
        )
    ):
        strategy = node.resolve('node')
        assert strategy.resolver == 'nodeenv'
        assert_can_run_js(strategy)


def test_update_path_env() -> None:
    """The _update_path_env() function correctly appends the target binary path to the PATH environment variable"""
    target = THIS_DIR / 'bin'
    if not target.exists():
        target.mkdir()

    sep = os.pathsep

    # known PATH separators - please update if need be
    assert sep in {':', ';'}

    # no env
    env = node._update_path_env(env=None, target_bin=target)
    assert env['PATH'].startswith(f'{target.absolute()}{sep}')

    # env without PATH
    env = node._update_path_env(
        env={'FOO': 'bar'},
        target_bin=target,
    )
    assert env['PATH'].startswith(f'{target.absolute()}{sep}')

    # env with empty PATH
    env = node._update_path_env(
        env={'PATH': ''},
        target_bin=target,
    )
    assert env['PATH'].startswith(f'{target.absolute()}{sep}')

    # env with set PATH without the separator postfix
    env = node._update_path_env(
        env={'PATH': '/foo'},
        target_bin=target,
    )
    assert env['PATH'] == f'{target.absolute()}{sep}/foo'

    # env with set PATH with the separator as a prefix
    env = node._update_path_env(
        env={'PATH': f'{sep}/foo'},
        target_bin=target,
    )
    assert env['PATH'] == f'{target.absolute()}{sep}/foo'

    # returned env included non PATH environment variables
    env = node._update_path_env(
        env={'PATH': '/foo', 'FOO': 'bar'},
        target_bin=target,
    )
    assert env['FOO'] == 'bar'
    assert env['PATH'] == f'{target.absolute()}{sep}/foo'

    # accepts a custom path separator
    env = node._update_path_env(
        env={'PATH': '/foo'},
        target_bin=target,
        sep='---',
    )
    assert env['PATH'] == f'{target.absolute()}---/foo'
