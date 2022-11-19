import os
import shutil
import subprocess
from typing import cast
from pathlib import Path

import pytest
from prisma.cli import _node as node
from prisma.cli._node import Target
from prisma._config import Config
from prisma._compat import nodejs

from ..utils import set_config


THIS_DIR = Path(__file__).parent

parametrize_target = pytest.mark.parametrize('target', ['node', 'npm'])


def _assert_can_run_js(strategy: node.Node) -> None:
    proc = strategy.run(
        str(THIS_DIR.joinpath('test.js')),
        stdout=subprocess.PIPE,
    )
    output = proc.stdout.decode('utf-8')
    assert output == 'Hello world!\n'


def _assert_can_run_npm(strategy: node.Node) -> None:
    assert strategy.target == 'npm'

    proc = strategy.run('help', stdout=subprocess.PIPE)
    output = proc.stdout.decode('utf-8')

    assert 'npm' in output


def assert_strategy(strategy: node.Node) -> None:
    if strategy.target == 'node':
        _assert_can_run_js(strategy)
    elif strategy.target == 'npm':
        _assert_can_run_npm(strategy)
    else:  # pragma: no cover
        raise ValueError(
            f'No tests implemented for strategy target: {strategy.target}'
        )


def test_resolve_bad_target() -> None:
    """resolve() raises a helpful error message when given an unknown target"""
    with pytest.raises(
        node.UnknownTargetError,
        match='Unknown target: foo; Valid choices are: node, npm',
    ):
        node.resolve(cast(node.Target, 'foo'))


@parametrize_target
@pytest.mark.skipif(nodejs is None, reason='nodejs-bin is not installed')
def test_nodejs_bin(target: Target) -> None:
    """When `nodejs-bin` is installed, it is resolved to and can be successfully used"""
    with set_config(
        Config.parse(
            use_nodejs_bin=True,
            use_global_node=False,
        )
    ):
        strategy = node.resolve(target)
        assert strategy.resolver == 'nodejs-bin'
        assert_strategy(strategy)


@parametrize_target
@pytest.mark.skipif(
    shutil.which('node') is None,
    reason='Node is not installed globally',
)
def test_resolves_binary_node(target: Target) -> None:
    """When `node` is installed globally, it is resolved to and can be successfully used"""
    with set_config(
        Config.parse(
            use_nodejs_bin=False,
            use_global_node=True,
        )
    ):
        strategy = node.resolve(target)
        assert strategy.resolver == 'global'
        assert_strategy(strategy)

    with set_config(
        Config.parse(
            use_nodejs_bin=False,
            use_global_node=False,
        )
    ):
        strategy = node.resolve(target)
        assert strategy.resolver == 'nodeenv'
        assert_strategy(strategy)


@parametrize_target
def test_nodeenv(target: Target) -> None:
    """When `nodejs-bin` and global `node` is not installed / configured to use, `nodeenv` is resolved to and can be successfully used"""
    with set_config(
        Config.parse(
            use_nodejs_bin=False,
            use_global_node=False,
        )
    ):
        strategy = node.resolve(target)
        assert strategy.resolver == 'nodeenv'
        assert_strategy(strategy)


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
