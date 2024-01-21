import pytest

import prisma
from prisma import Prisma

from ..utils import RawQueries, DatabaseConfig


def test_base_usage(client: Prisma) -> None:
    """Basic non context manager usage"""
    batcher = client.batch_()
    batcher.user.create({'name': 'Robert'})
    batcher.user.create({'name': 'Tegan'})
    batcher.commit()

    user = client.user.find_first(where={'name': 'Robert'})
    assert user is not None
    assert user.name == 'Robert'

    user = client.user.find_first(where={'name': 'Tegan'})
    assert user is not None
    assert user.name == 'Tegan'


def test_context_manager(client: Prisma) -> None:
    """Basic usage with a context manager"""
    with client.batch_() as batcher:
        batcher.user.create({'name': 'Robert'})
        batcher.user.create({'name': 'Tegan'})

    user = client.user.find_first(where={'name': 'Robert'})
    assert user is not None
    assert user.name == 'Robert'

    user = client.user.find_first(where={'name': 'Tegan'})
    assert user is not None
    assert user.name == 'Tegan'


def test_batch_error(client: Prisma) -> None:
    """Error while committing does not commit any records"""
    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        batcher = client.batch_()
        batcher.user.create({'id': 'abc', 'name': 'Robert'})
        batcher.user.create({'id': 'abc', 'name': 'Robert 2'})
        batcher.commit()

    assert exc.match(r'Unique constraint failed')
    assert client.user.count() == 0


def test_context_manager_error(client: Prisma) -> None:
    """Error exiting context manager does not commit any records"""
    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        with client.batch_() as batcher:
            batcher.user.create({'id': 'abc', 'name': 'Robert'})
            batcher.user.create({'id': 'abc', 'name': 'Robert 2'})

    assert exc.match(r'Unique constraint failed')
    assert client.user.count() == 0


def test_context_manager_throws_error(client: Prisma) -> None:
    """Context manager respects errors"""
    with pytest.raises(RuntimeError) as exc:
        with client.batch_() as batcher:
            batcher.user.create({'name': 'Robert'})
            raise RuntimeError('Example error')

    assert exc.match('Example error')
    assert client.user.count() == 0


def test_mixing_models(client: Prisma) -> None:
    """Batching queries to multiple models works as intended"""
    with client.batch_() as batcher:
        # NOTE: this is just to test functionality, the better method
        # for acheiving this is to use nested writes with user.create
        # client.user.create({'name': 'Robert', 'profile': {'create': {'bio': 'Robert\'s profile'}}})
        batcher.user.create({'id': 'abc', 'name': 'Robert'})
        batcher.profile.create(
            {
                'user': {'connect': {'id': 'abc'}},
                'description': "Robert's profile",
                'country': 'Scotland',
            }
        )

    user = client.user.find_first(where={'name': 'Robert'}, include={'profile': True})
    assert user is not None
    assert user.name == 'Robert'
    assert user.profile is not None
    assert user.profile.description == "Robert's profile"

    assert client.user.count() == 1
    assert client.profile.count() == 1


def test_mixing_actions(client: Prisma) -> None:
    """Batching queries to different operations works as intended"""
    with client.batch_() as batcher:
        batcher.user.create({'name': 'Robert'})
        batcher.user.delete_many(where={'name': 'Robert'})

    assert client.user.count() == 0


def test_reusing_batcher(client: Prisma) -> None:
    """Reusing the same batcher does not commit the same query multiple times"""
    batcher = client.batch_()
    batcher.user.create({'name': 'Robert'})
    batcher.commit()

    assert client.user.count() == 1

    batcher.user.create({'name': 'Robert 2'})
    batcher.commit()

    assert client.user.count() == 2


def test_large_query(client: Prisma) -> None:
    """Batching a lot of queries works"""
    with client.batch_() as batcher:
        for i in range(1000):
            batcher.user.create({'name': f'User {i}'})

    assert client.user.count() == 1000


def test_delete(client: Prisma) -> None:
    """delete action works as suggested"""
    user = client.user.create({'name': 'Robert'})
    assert client.user.find_first(where={'id': user.id}) is not None

    with client.batch_() as batcher:
        batcher.user.delete(where={'id': user.id})

    assert client.user.find_first(where={'id': user.id}) is None


def test_update(client: Prisma) -> None:
    """update action works as suggested"""
    user = client.user.create({'name': 'Robert'})
    assert client.user.find_first(where={'id': user.id}) is not None

    with client.batch_() as batcher:
        batcher.user.update(where={'id': user.id}, data={'name': 'Roberto'})

    new = client.user.find_first(where={'id': user.id})
    assert new is not None
    assert new.id == user.id
    assert new.name == 'Roberto'


def test_upsert(client: Prisma) -> None:
    """upsert action works as suggested"""
    user_id = 'abc123'
    assert client.user.find_unique(where={'id': user_id}) is None

    with client.batch_() as batcher:
        batcher.user.upsert(
            where={'id': user_id},
            data={
                'create': {'id': user_id, 'name': 'Robert'},
                'update': {'name': 'Robert'},
            },
        )

    user = client.user.find_unique(where={'id': user_id})
    assert user is not None
    assert user.id == user_id
    assert user.name == 'Robert'

    with client.batch_() as batcher:
        batcher.user.upsert(
            where={'id': user_id},
            data={
                'create': {'id': user_id, 'name': 'Robert'},
                'update': {'name': 'Roberto'},
            },
        )

    user = client.user.find_unique(where={'id': user_id})
    assert user is not None
    assert user.id == user_id
    assert user.name == 'Roberto'
    assert client.user.count() == 1


def test_update_many(client: Prisma) -> None:
    """update_many action works as suggested"""
    client.user.create({'name': 'Robert'})
    client.user.create({'name': 'Robert 2'})

    with client.batch_() as batcher:
        batcher.user.update_many(where={'name': {'startswith': 'Robert'}}, data={'name': 'Robert'})

    users = client.user.find_many()
    assert len(users) == 2
    assert users[0].name == 'Robert'
    assert users[1].name == 'Robert'


def test_delete_many(client: Prisma) -> None:
    """delete_many action works as suggested"""
    client.user.create({'name': 'Robert'})
    client.user.create({'name': 'Robert 2'})
    assert client.user.count() == 2

    with client.batch_() as batcher:
        batcher.user.delete_many(where={'name': {'startswith': 'Robert'}})

    assert client.user.count() == 0


def test_execute_raw(client: Prisma, raw_queries: RawQueries) -> None:
    """execute_raw action can be used to execute raw SQL queries"""
    post1 = client.post.create(
        {
            'title': 'My first post!',
            'published': False,
        }
    )
    post2 = client.post.create(
        {
            'title': 'My 2nd post.',
            'published': False,
        }
    )

    with client.batch_() as batcher:
        batcher.execute_raw(
            raw_queries.update_unique_post_title,
            post1.id,
        )
        batcher.execute_raw(
            raw_queries.update_unique_post_new_title,
            post2.id,
        )

    found = client.post.find_unique(where={'id': post1.id})
    assert found is not None
    assert found.id == post1.id
    assert found.title == 'My edited title'

    found = client.post.find_unique(where={'id': post2.id})
    assert found is not None
    assert found.id == post2.id
    assert found.title == 'My new title'


def test_create_many_unsupported(
    client: Prisma,
    config: DatabaseConfig,
) -> None:
    """Cannot call create_many on databases that do not support it"""
    if 'create_many' not in config.unsupported_features:
        pytest.skip('The create_many method is supported by the current behaviour')

    with pytest.raises(prisma.errors.UnsupportedDatabaseError) as exc:
        with client.batch_() as batcher:
            batcher.user.create_many([{'name': 'Robert'}])

    assert exc.match(r'create_many\(\) is not supported')
