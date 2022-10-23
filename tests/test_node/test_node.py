import shutil
import subprocess
from typing import cast
from pathlib import Path

import pytest
from prisma.cli import _node as node
from prisma._config import Config

from ..utils import set_config


def assert_can_run_js(strategy: node.Node) -> None:
    proc = strategy.run(
        str(Path(__file__).parent.joinpath('test.js')),
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
    shutil.which('node') is not None,
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
