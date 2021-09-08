from prisma import Client


def test_basic(client: Client) -> None:
    """Basic call to create, just here as a placeholder, more tests should be added"""
    user = client.user.create({'name': 'Robert'})
    assert user.name == 'Robert'
