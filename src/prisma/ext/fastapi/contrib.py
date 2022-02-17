from typing import Optional
from fastapi import FastAPI


from ...client import Client


def register_prisma(app: FastAPI, client: Optional[Client] = None) -> None:
    if client is None:
        client = Client(auto_register=True)

    @app.on_event('startup')  # type: ignore
    async def _() -> None:
        if not client.is_connected():
            await client.connect()

    @app.on_event('shutdown')  # type: ignore
    async def _() -> None:
        if client.is_connected():
            await client.disconnect()
