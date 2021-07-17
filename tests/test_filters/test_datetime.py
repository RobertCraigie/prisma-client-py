import datetime

import pytest
from prisma import Client
from prisma.models import Post


@pytest.fixture(name='post', scope='session')
async def post_fixture(client: Client) -> Post:
    return await client.post.create({'title': 'Foo', 'published': False})


@pytest.mark.asyncio
async def test_finds_post(client: Client, post: Post) -> None:
    found = await client.post.find_first(
        where={'created_at': {'lt': post.created_at + datetime.timedelta(seconds=1)}}
    )
    assert found is not None
    assert found.title == 'Foo'


@pytest.mark.asyncio
@pytest.mark.persist_data
async def test_tz_aware(client: Client, post: Post) -> None:
    found = await client.post.find_first(
        where={
            'created_at': {
                'lt': (post.created_at + datetime.timedelta(hours=1)).astimezone(
                    datetime.timezone.max
                )
            }
        }
    )
    assert found is not None
    assert found.title == 'Foo'
