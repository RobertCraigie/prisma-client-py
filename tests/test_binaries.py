import os
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from prisma.utils import temp_env_update
from prisma.binaries import BINARIES, ENGINES, Engine
from prisma.binaries.constants import PRISMA_CLI_NAME


def test_skips_cached_binary(caplog: LogCaptureFixture) -> None:
    """Downloading an already existing binary does not actually do anything"""

    if os.environ.get('PRISMA_CUSTOM_BINARIES'):
        pytest.skip('unsupported configuration')

    # NOTE: this is not a great way to test this
    binary = BINARIES[0]
    binary.download()
    assert 'is cached' in caplog.records[0].message


@pytest.mark.parametrize('engine', ENGINES)
def test_engine_resolves_env_override(engine: Engine) -> None:
    """Env variables override the default path for an engine binary"""
    with temp_env_update({engine.env: 'foo'}):
        assert engine.path == Path('foo')


def test_cli_binary_resolves_env_override() -> None:
    """Env variable overrides the default path for the CLI binary"""
    binary = BINARIES[-1]
    assert binary.name == PRISMA_CLI_NAME
    with temp_env_update({binary.env: 'foo'}):
        assert binary.path == Path('foo')
