from fastapi import FastAPI

from . import routes


app = FastAPI(
    title="Prisma Admin",
    description='A FastAPI admin dashboard with Prisma and Tabler UI',
)
app.include_router(routes.router)
