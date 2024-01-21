from prisma import Prisma

# TODO: more tests


def test_delete_many(client: Prisma) -> None:
    """Standard usage"""
    posts = [
        client.post.create({'title': 'Foo post', 'published': False}),
        client.post.create({'title': 'Bar post', 'published': False}),
    ]
    count = client.post.delete_many()
    assert count >= 1

    for post in posts:
        assert client.post.find_unique(where={'id': post.id}) is None
