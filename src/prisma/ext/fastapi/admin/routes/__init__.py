from fastapi import APIRouter

from . import resources


router = APIRouter()
router.include_router(resources.router)
