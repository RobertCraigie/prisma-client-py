from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Mapping, Optional, cast

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from prisma.models import User

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
AUTH_TOKEN = '_AUTH_TOKEN'


class Token(BaseModel):
    access_token: str
    token_type: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user(username: str):
    return await User.prisma().find_unique(
        where={
            'username': username,
        },
    )


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_authorizer(*, required: bool = True) -> Callable[..., Any]:
    return _get_current_user if required else _get_current_optional_user


def _get_token(request: Request) -> Optional[str]:
    # TODO: is storing tokens like this secure?
    return request.cookies.get(AUTH_TOKEN)


async def _get_current_optional_user(
    token: Optional[str] = Depends(_get_token),
) -> Optional[User]:
    if token is None:
        return None

    try:
        return await _get_current_user(token)
    except HTTPException:
        return None


async def _get_current_user(token: Optional[str] = Depends(_get_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    try:
        payload = cast(
            Mapping[str, str], jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(username=username)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(_get_current_user)):
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
