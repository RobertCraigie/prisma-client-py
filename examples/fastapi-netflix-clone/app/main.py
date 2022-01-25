from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from prisma import Client, get_client as get_prisma
from prisma.errors import ClientNotRegisteredError

from . import routes


app = FastAPI()


@app.on_event('startup')  # type: ignore
async def startup() -> None:
    prisma = Client(auto_register=True)
    await prisma.connect()


@app.on_event('shutdown')  # type: ignore
async def shutdown() -> None:
    try:
        prisma = get_prisma()
    except ClientNotRegisteredError:
        return

    if prisma.is_connected():
        await prisma.disconnect()


app.include_router(routes.auth.router)
app.include_router(routes.index.router)
app.include_router(routes.profile.router)
app.mount('/static', StaticFiles(directory='static'), name='static')
