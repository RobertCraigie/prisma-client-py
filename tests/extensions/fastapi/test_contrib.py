from fastapi import FastAPI
from prisma import Client
from prisma.ext.fastapi import register_prisma


def test_registers_events() -> None:
    app = FastAPI()
    assert len(app.router.on_startup) == 0
    assert len(app.router.on_shutdown) == 0

    register_prisma(app, Client())

    assert len(app.router.on_startup) == 1
    assert len(app.router.on_shutdown) == 1
