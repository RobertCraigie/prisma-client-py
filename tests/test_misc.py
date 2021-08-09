import pytest
from _pytest.capture import CaptureFixture

import prisma
from prisma import Client
from prisma.models import User

from .utils import Testdir


def test_create_partial_raises_outside_generation() -> None:
    with pytest.raises(RuntimeError) as exc:
        User.create_partial('PartialUser', exclude={'name'})
    assert 'outside of client generation' in str(exc.value)


@pytest.mark.asyncio
async def test_query_logging_disabled(
    client: Client, capsys: CaptureFixture[str]
) -> None:
    await client.user.create({'name': 'Robert'})
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == ''


@pytest.mark.asyncio
async def test_logs_sql_queries(testdir: Testdir) -> None:
    client = Client(log_queries=True)

    # we have to redirect stdout to a file to capture it as
    # we are passing stdout to a subprocess
    with testdir.redirect_stdout_to_file() as file:
        await client.connect()

        # implementation detail of this test
        with pytest.raises(prisma.errors.TableNotFoundError):
            await client.user.find_unique(where={'id': 'jsdhsjd'})

        await client.disconnect()

    assert 'SELECT `main`.`User`.`id' in file.read_text()
