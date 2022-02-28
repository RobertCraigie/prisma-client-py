"""Basic FastAPI app for CRUD operations on users and posts using Prisma Client Python"""
from typing import Optional, List

from fastapi import FastAPI
from prisma import Prisma
from prisma.models import User, Post
from prisma.types import UserUpdateInput
from prisma.partials import UserWithoutRelations, PostWithoutRelations


app = FastAPI()
prisma = Prisma(auto_register=True)


@app.on_event('startup')  # type: ignore
async def startup() -> None:
    await prisma.connect()


@app.on_event('shutdown')  # type: ignore
async def shutdown() -> None:
    if prisma.is_connected():
        await prisma.disconnect()


@app.get(
    '/users',
    response_model=List[UserWithoutRelations],
)
async def list_users(take: int = 10) -> List[User]:
    return await User.prisma().find_many(take=take)


@app.post(
    '/users',
    response_model=UserWithoutRelations,
)
async def create_user(name: str, email: Optional[str] = None) -> User:
    return await User.prisma().create({'name': name, 'email': email})


@app.put(
    '/users/{user_id}',
    response_model=UserWithoutRelations,
)
async def update_user(
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[User]:
    data: UserUpdateInput = {}

    if name is not None:
        data['name'] = name

    if email is not None:
        data['email'] = email

    return await User.prisma().update(
        where={
            'id': user_id,
        },
        data=data,
    )


@app.delete(
    '/users/{user_id}',
    response_model=User,
)
async def delete_user(user_id: str) -> Optional[User]:
    return await User.prisma().delete(
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
async def get_user(user_id: str) -> Optional[User]:
    return await User.prisma().find_unique(
        where={
            'id': user_id,
        },
    )


@app.get(
    '/users/{user_id}/posts',
    response_model=List[PostWithoutRelations],
)
async def get_user_posts(user_id: str) -> List[Post]:
    user = await User.prisma().find_unique(
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
async def create_post(user_id: str, title: str, published: bool) -> Post:
    return await Post.prisma().create(
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
async def list_posts(take: int = 10) -> List[Post]:
    return await Post.prisma().find_many(take=take)


@app.get(
    '/posts/{post_id}',
    response_model=Post,
)
async def get_post(post_id: str) -> Optional[Post]:
    return await Post.prisma().find_unique(
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
async def delete_post(post_id: str) -> Optional[Post]:
    return await Post.prisma().delete(
        where={
            'id': post_id,
        },
        include={
            'author': True,
        },
    )
