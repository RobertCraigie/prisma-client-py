from typing import Any, Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from prisma.models import User

from ._utils import templates
from ..dependencies import get_current_user_authorizer


router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def home(
    request: Request,
    user: Optional[User] = Depends(get_current_user_authorizer(required=False)),
) -> Any:
    if user is not None:
        return RedirectResponse('/profile')

    return templates.TemplateResponse(
        'index.html.jinja', {'request': request, 'user': user}
    )
