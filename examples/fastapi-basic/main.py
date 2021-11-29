"""Basic FastAPI app for CRUD operations on users and posts using Prisma Client Python"""
from typing import Optional, List, cast

from fastapi import FastAPI, Request, Depends
from prisma import Client
from prisma.models import User, Post
from prisma.types import UserUpdateInput
from prisma.partials import UserWithoutRelations, PostWithoutRelations


app = FastAPI()


def get_client(request: Request) -> Client:
    return cast(Client, request.app.state.db)


@app.on_event('startup')  # type: ignore
async def startup() -> None:
    app.state.db = db = Client()
    await db.connect()


@app.get(
    '/users',
    response_model=List[UserWithoutRelations],
)
async def list_users(take: int = 10, db: Client = Depends(get_client)) -> List[User]:
    return await db.user.find_many(take=take)


@app.post(
    '/users',
    response_model=UserWithoutRelations,
)
async def create_user(
    name: str, email: Optional[str] = None, db: Client = Depends(get_client)
) -> User:
    return await db.user.create({'name': name, 'email': email})


@app.put(
    '/users/{user_id}',
    response_model=UserWithoutRelations,
)
async def update_user(
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    db: Client = Depends(get_client),
) -> Optional[User]:
    data: UserUpdateInput = {}

    if name is not None:
        data['name'] = name

    if email is not None:
        data['email'] = email

    return await db.user.update(
        where={
            'id': user_id,
        },
        data=data,
    )


@app.delete(
    '/users/{user_id}',
    response_model=User,
)
async def delete_user(user_id: str, db: Client = Depends(get_client)) -> Optional[User]:
    return await db.user.delete(
        where={
            'id': user_id,
        },
        include={
            'posts': True,
        },
    )


@app.get(
    '/users/{user_id}',
    response_model=UserWithoutRelations,
)
async def get_user(user_id: str, db: Client = Depends(get_client)) -> Optional[User]:
    return await db.user.find_unique(
        where={
            'id': user_id,
        },
    )


@app.get(
    '/users/{user_id}/posts',
    response_model=List[PostWithoutRelations],
)
async def get_user_posts(user_id: str, db: Client = Depends(get_client)) -> List[Post]:
    user = await db.user.find_unique(
        where={
            'id': user_id,
        },
        include={
            'posts': True,
        },
    )
    if user is not None:
        # we are including the posts, so they will never be None
        assert user.posts is not None
        return user.posts
    return []


@app.post(
    '/users/{user_id}/posts',
    response_model=PostWithoutRelations,
)
async def create_post(
    user_id: str, title: str, published: bool, db: Client = Depends(get_client)
) -> Post:
    return await db.post.create(
        data={
            'title': title,
            'published': published,
            'author': {
                'connect': {
                    'id': user_id,
                },
            },
        }
    )


@app.get(
    '/posts',
    response_model=List[PostWithoutRelations],
)
async def list_posts(take: int = 10, db: Client = Depends(get_client)) -> List[Post]:
    return await db.post.find_many(take=take)


@app.get(
    '/posts/{post_id}',
    response_model=Post,
)
async def get_post(post_id: str, db: Client = Depends(get_client)) -> Optional[Post]:
    return await db.post.find_unique(
        where={
            'id': post_id,
        },
        include={
            'author': True,
        },
    )


@app.delete(
    '/posts/{post_id}',
    response_model=Post,
)
async def delete_post(post_id: str, db: Client = Depends(get_client)) -> Optional[Post]:
    return await db.post.delete(
        where={
            'id': post_id,
        },
        include={
            'author': True,
        },
    )
