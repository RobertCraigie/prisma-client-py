from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from prisma.models import User, Profile, Movie

from ._utils import templates
from ..dependencies import get_current_user_authorizer


router = APIRouter(prefix='/profile')


@router.get('/', response_class=HTMLResponse)
async def profile(
    request: Request, user: User = Depends(get_current_user_authorizer())
) -> Any:
    profiles = await Profile.prisma().find_many(
        where={
            'user_id': user.id,
        },
    )
    return templates.TemplateResponse(
        'profileList.html.jinja',
        {'profiles': profiles, 'user': user, 'request': request},
    )


@router.get('/watch/{profile_id}', response_class=HTMLResponse)
async def watch(
    request: Request,
    profile_id: str,
    user: User = Depends(get_current_user_authorizer()),
) -> Any:
    profile = await Profile.prisma().find_unique(
        where={
            'id': profile_id,
        },
        include={
            'user': True,
        },
    )
    if profile is None:
        return RedirectResponse('/')

    assert profile.user is not None
    if profile.user.id != user.id:
        return RedirectResponse('/profile')

    movies = await Movie.prisma().find_many(
        where={
            'age_limit': profile.age_limit,
        },
    )
    showcase = movies[0] if movies else None

    return templates.TemplateResponse(
        'movieList.html.jinja',
        {'movies': movies, 'showcase': showcase, 'user': user, 'request': request},
    )
