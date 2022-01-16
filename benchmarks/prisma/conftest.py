from prisma import Client


def pytest_sessionstart() -> None:
    client = Client(auto_register=True)
    client.connect()
