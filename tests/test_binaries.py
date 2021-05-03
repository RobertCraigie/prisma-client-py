from _pytest.logging import LogCaptureFixture

from prisma.binaries import BINARIES


def test_skips_cached_binary(caplog: LogCaptureFixture) -> None:
    # NOTE: this is not a great way to test this
    binary = BINARIES[0]
    binary.download()
    assert 'is cached' in caplog.records[0].message
