from prisma import Client


def test_basic(client: Client) -> None:
    user = client.user.create({'name': 'Robert'})
    assert user.name == 'Robert'
