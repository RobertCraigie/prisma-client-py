import pytest
from prisma import Client


# TODO: more tests
# TODO: test batch within transaction


def test_context_manager(client: Client) -> None:
    with client.tx() as transaction:
        user = transaction.user.create({'name': 'Robert'})
        assert user.name == 'Robert'

        # ensure not commited outside transaction
        assert client.user.count() == 0

        transaction.profile.create(
            {'bio': 'Hello, there!', 'user_id': user.id}
        )

    found = client.user.find_unique(
        where={'id': user.id}, include={'profile': True}
    )
    assert found is not None
    assert found.name == 'Robert'
    assert found.profile is not None
    assert found.profile.bio == 'Hello, there!'


def test_context_manager_auto_rollback(client: Client) -> None:
    with pytest.raises(RuntimeError) as exc:
        with client.tx() as tx:
            user = tx.user.create({'name': 'Tegan'})
            raise RuntimeError('Error ocurred mid transaction.')

    assert exc.match('Error ocurred mid transaction.')
    found = client.user.find_unique(where={'id': user.id})
    assert found is None
