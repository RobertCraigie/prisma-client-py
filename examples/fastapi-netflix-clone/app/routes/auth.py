from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from prisma.models import User

from ..dependencies.auth import (
    AUTH_TOKEN,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    authenticate_user,
    create_access_token,
    get_password_hash,
)


router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(AUTH_TOKEN, access_token)
    return {"access_token": access_token, "token_type": "bearer"}


# TODO: this should return a HtmlResponse
@router.get('/auth/signup')
async def signup(
    username: str,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
) -> User:
    # TODO: handle unique violation
    return await User.prisma().create(
        data={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'hashed_password': get_password_hash(password),
        }
    )


@router.get('/auth/signout', response_class=RedirectResponse)
async def signout(response: Response) -> RedirectResponse:
    response.delete_cookie(AUTH_TOKEN)
    return RedirectResponse('/')
