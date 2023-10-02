# pyright: reportGeneralTypeIssues=false
# pyright: reportUnknownLambdaType=false

import pytest
from datetime import timedelta
from unittest.mock import patch
from prisma import Prisma, models
from prisma.decorator import use_prisma


_USER_ID: str = 'user_123_id'
_USER_NAME: str = 'user_123_name'


@pytest.mark.asyncio
async def test_use_prisma_decorator():
    """
    Testing the use_prisma decorator which provides an auto-connecting and
    auto-disconnecting Prisma client to the function it decorates.
    """
    # The reason for why we call all tests like this, is because we cannot stack
    # the @use_prisma decorator together with the @pytest.mark.asyncio decorator.
    await _create_user()
    await _get_user()
    await _delete_user()
    await _with_client_name_arg()
    await _with_connect_timeout_arg()
    await _with_invalid_prisma_arg()


@use_prisma
async def _create_user(db: Prisma):
    await db.user.create(data={'id': _USER_ID, 'name': _USER_NAME})


@use_prisma
async def _get_user(db: Prisma):
    user: models.User = await db.user.find_first(where={'id': _USER_ID})
    assert user.name == _USER_NAME


@use_prisma
async def _delete_user(db: Prisma):
    await db.user.delete(where={'id': _USER_ID})


@use_prisma(name='client')
async def _with_client_name_arg(client: Prisma):
    assert isinstance(client, Prisma)
    assert client.is_connected()


@use_prisma(connect_timeout=timedelta(seconds=42), name='prisma')
async def _with_connect_timeout_arg(prisma: Prisma):
    assert isinstance(prisma, Prisma)
    assert prisma.is_connected()
    assert prisma._connect_timeout == timedelta(seconds=42)


async def _with_invalid_prisma_arg():
    # the patch below will prevent the effect of garbage collection of the Prisma instance
    # which would lead to an additional AttributeError
    with patch.object(Prisma, '__del__', lambda _: None):

        with pytest.raises(TypeError) as exc:

            @use_prisma(
                invalid_arg='random'
            )  # provide an invalid argument name 'invalid_arg' to Prisma
            async def _(db: Prisma):
                await db.user.create(data={'id': _USER_ID, 'name': _USER_NAME})

            await _()

        assert (
            "__init__() got an unexpected keyword argument 'invalid_arg'"
            in str(exc)
        )
