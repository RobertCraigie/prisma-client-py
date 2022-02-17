from fastapi import FastAPI

from . import routes
from .models import Admin
from .providers.auth import BaseAuthProvider


# TODO: refactor this, it's difficult to type


class PrismaAdmin(FastAPI):
    def configure(
        self,
        *,
        admin_model: Admin,
        auth_provider: BaseAuthProvider,
    ) -> None:
        self.admin_model = admin_model
        self.auth_provider = auth_provider


app = PrismaAdmin(
    title='Prisma Admin',
    version='0.1.0',
    description='A FastAPI admin dashboard with Prisma and Tabler UI',
)
app.include_router(routes.router)
