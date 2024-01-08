from prisma import Prisma


def test_update_many(client: Prisma) -> None:
    """Filters update correct records

    TODO: refactor this test, its a messs
    """
    posts = [
        client.post.create({'title': 'Test post 1', 'published': False}),
        client.post.create({'title': 'Test post 2', 'published': False}),
    ]
    count = client.post.update_many(where={'published': False}, data={'published': True})
    assert count == 2

    post = client.post.find_unique(where={'id': posts[0].id})
    assert post is not None
    assert post.published is True

    count = client.post.update_many(where={'published': False}, data={'published': True})
    assert count == 0

    count = client.post.update_many(where={'id': posts[0].id}, data={'published': False})
    assert count == 1

    post = client.post.find_unique(where={'id': posts[0].id})
    assert post is not None
    assert post.published is False

    count = client.post.update_many(where={'published': False}, data={'views': 10})
    assert count == 1

    post = client.post.find_unique(where={'id': posts[0].id})
    assert post is not None
    assert post.views == 10

    count = client.post.update_many(where={'id': posts[0].id}, data={'id': 'sdhajd'})
    assert count == 1

    post = client.post.find_unique(where={'id': 'sdhajd'})
    assert post is not None

    post = client.post.find_unique(where={'id': posts[0].id})
    assert post is None


def test_setting_to_null(client: Prisma) -> None:
    """Setting a field to None sets the database record to None"""
    post = client.post.create(
        data={
            'title': 'Foo',
            'published': True,
            'description': 'Description',
        }
    )
    assert post.description == 'Description'

    count = client.post.update_many(
        where={},
        data={'description': None},
    )
    assert count == 1

    found = client.post.find_unique(where={'id': post.id})
    assert found is not None
    assert found.id == post.id
    assert found.title == 'Foo'
    assert found.description is None
