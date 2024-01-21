import pytest

import prisma
from prisma import Prisma


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

    assert exc.match(r'Unique constraint failed on the fields: \(`id`\)')
    assert client.user.count() == 0


def test_context_manager_error(client: Prisma) -> None:
    """Error exiting context manager does not commit any records"""
    with pytest.raises(prisma.errors.UniqueViolationError) as exc:
        with client.batch_() as batcher:
            batcher.user.create({'id': 'abc', 'name': 'Robert'})
            batcher.user.create({'id': 'abc', 'name': 'Robert 2'})

    assert exc.match(r'Unique constraint failed on the fields: \(`id`\)')
    assert client.user.count() == 0


def test_commit(client: Prisma) -> None:
    """Commits created records"""
    with client.batch_() as batcher:
        batcher.user.create({'name': 'Robert'})
        assert client.user.count() == 0

    assert client.user.count() == 1
