import pytest
from _pytest.capture import CaptureFixture

import prisma
from prisma import Prisma
from prisma.models import User

from .utils import Testdir


def test_create_partial_raises_outside_generation() -> None:
    """Trying to create a partial type outside of client generation raises an error"""
    with pytest.raises(RuntimeError) as exc:
        User.create_partial('PartialUser', exclude={'name'})
    assert 'outside of client generation' in str(exc.value)


@pytest.mark.asyncio
async def test_query_logging_disabled(
    client: Prisma, capsys: CaptureFixture[str]
) -> None:
    """No queries are logged when query logging is disabled"""
    await client.user.create({'name': 'Robert'})
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == ''


@pytest.mark.asyncio
async def test_logs_sql_queries(testdir: Testdir) -> None:
    """SQL queries are logged when enabled"""
    client = Prisma(log_queries=True)

    # we have to redirect stdout to a file to capture it as
    # we are passing stdout to a subprocess
    with testdir.redirect_stdout_to_file() as file:
        await client.connect()

        # implementation detail of this test
        with pytest.raises(prisma.errors.TableNotFoundError):
            await client.user.find_unique(where={'id': 'jsdhsjd'})

        await client.disconnect()

    assert 'SELECT `main`.`User`.`id' in file.read_text()


@pytest.mark.asyncio
async def test_unmarked_test_disallowed_client() -> None:
    """Test case that isn't marked with @pytest.mark.prisma cannot access the client"""
    with pytest.raises(RuntimeError) as exc:
        await User.prisma().create({'name': 'Robert'})

    assert '@pytest.mark.prisma' in exc.value.args[0]
