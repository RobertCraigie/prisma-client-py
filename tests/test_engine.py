from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from prisma import Client
from prisma.engine import errors, utils


@pytest.mark.asyncio
async def test_engine_connects() -> None:
    db = Client()
    await db.connect()

    with pytest.raises(errors.AlreadyConnectedError):
        await db.connect()

    await db.disconnect()


def test_engine_binary_does_not_exist(monkeypatch: MonkeyPatch) -> None:
    def mock_exists(path: Path) -> bool:
        return False

    monkeypatch.setattr(Path, 'exists', mock_exists, raising=True)

    with pytest.raises(errors.BinaryNotFoundError) as exc:
        utils.ensure()

    assert exc.match(
        r'Expected .* or .* but neither were found\.\nTry running prisma py fetch'
    )
