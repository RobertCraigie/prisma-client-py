import datetime

import pytest

from prisma import Client


# TODO: add tests for every database provider we support


@pytest.mark.asyncio
async def test_precision_loss(client: Client) -> None:
    """https://github.com/RobertCraigie/prisma-client-py/issues/129"""
    date = datetime.datetime.utcnow()
    post = await client.post.create(
        data={
            'title': 'My first post',
            'published': False,
            'created_at': date,
        },
    )
    found = await client.post.find_first(
        where={
            'created_at': date,
        },
    )
    assert found is not None

    found = await client.post.find_first(
        where={
            'created_at': post.created_at,
        },
    )
    assert found is not None
