import pytest

from prisma import Prisma


@pytest.mark.asyncio
async def test_warn_when_connect_timeout_is_int() -> None:
    """Ensure that `calling Prisma(connect_timeout:int)` emit a warning

    https://github.com/RobertCraigie/prisma-client-py/issues/167
    """
    with pytest.warns(DeprecationWarning):
        Prisma(connect_timeout=10)


@pytest.mark.asyncio
async def test_warn_when_calling_connect_with_int_timeout() -> None:
    """Ensure that calling `client.connect(timeout:int)` emit a warning

    https://github.com/RobertCraigie/prisma-client-py/issues/167
    """
    client = Prisma()
    with pytest.warns(DeprecationWarning):
        await client.connect(timeout=10)


@pytest.mark.asyncio
async def test_warn_when_calling_disconnect_with_float_timeout() -> None:
    """Ensure that calling `client.disconnect(timeout:float)` emit a warning

    https://github.com/RobertCraigie/prisma-client-py/issues/167
    """
    client = Prisma()
    await client.connect()
    with pytest.warns(DeprecationWarning):
        await client.disconnect(timeout=5.0)


@pytest.mark.asyncio
async def test_warn_when_calling_tx_with_int_max_wait() -> None:
    """Ensure that calling `client.tx(max_wait:int)` emit a warning

    https://github.com/RobertCraigie/prisma-client-py/issues/167
    """
    client = Prisma()
    await client.connect()
    with pytest.warns(DeprecationWarning):
        client.tx(max_wait=2000)


@pytest.mark.asyncio
async def test_warn_when_calling_tx_with_int_timeout() -> None:
    """Ensure that calling `client.tx(timeout:int)` emit a warning

    https://github.com/RobertCraigie/prisma-client-py/issues/167
    """
    client = Prisma()
    await client.connect()
    with pytest.warns(DeprecationWarning):
        client.tx(timeout=5000)
