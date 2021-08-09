from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from prisma.binaries import BINARIES, ENGINES, Engine
from prisma.utils import temp_env_update


def test_skips_cached_binary(caplog: LogCaptureFixture) -> None:
    # NOTE: this is not a great way to test this
    binary = BINARIES[0]
    binary.download()
    assert 'is cached' in caplog.records[0].message


@pytest.mark.parametrize('engine', ENGINES)
def test_engine_resolves_env_override(engine: Engine) -> None:
    # TODO: should be able to override binary resolving as well
    with temp_env_update({engine.env: 'foo'}):
        assert engine.path == Path('foo')
