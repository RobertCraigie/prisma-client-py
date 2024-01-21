import pytest

from prisma.models import User

from ..utils import RawQueries


async def create_user() -> User:
    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
    )
    assert isinstance(user, User)
    return user


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_create() -> None:
    """Creating a record using model-based access"""
    user = await User.prisma().create({'name': 'Robert'})
    assert isinstance(user, User)
    assert user.name == 'Robert'

    user = await User.prisma().create(
        data={
            'name': 'Tegan',
            'posts': {
                'create': {
                    'title': 'My first post!',
                    'published': True,
                },
            },
        },
        include={
            'posts': True,
        },
    )
    assert user.name == 'Tegan'
    assert user.posts is not None
    assert len(user.posts) == 1
    assert user.posts[0].title == 'My first post!'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_delete() -> None:
    """Deleting a record using model-based access"""
    deleted = await User.prisma().delete(
        where={
            'id': 'abc',
        },
    )
    assert deleted is None

    user = await User.prisma().create({'name': 'Robert'})
    assert isinstance(user, User)

    deleted2 = await User.prisma().delete(
        where={
            'id': user.id,
        },
    )
    assert deleted2 is not None
    assert deleted2.name == 'Robert'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_find_unique() -> None:
    """Finding a unique record using model-based access"""
    found = await User.prisma().find_unique(
        where={
            'id': 'abc',
        },
    )
    assert found is None

    user = await create_user()
    found = await User.prisma().find_unique(
        where={
            'id': user.id,
        },
    )
    assert found is not None
    assert found.name == 'Robert'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_find_many() -> None:
    """Finding many records using model-based access"""
    users = [
        await User.prisma().create({'name': 'Robert'}),
        await User.prisma().create({'name': 'Robert 2'}),
        await User.prisma().create({'name': 'Tegan'}),
    ]

    found = await User.prisma().find_many(
        where={
            'name': {
                'startswith': 'Robert',
            },
        },
        order={
            'id': 'asc',
        },
    )
    assert len(found) == 2
    assert found[0].id == users[0].id
    assert found[1].id == users[1].id


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_find_first() -> None:
    """Finding a record using model-based access"""
    found = await User.prisma().find_first(where={'name': 'Robert'})
    assert found is None

    await create_user()

    found = await User.prisma().find_first(where={'name': 'Robert'})
    assert found is not None
    assert found.name == 'Robert'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_update() -> None:
    """Updating a record using model-based access"""
    user = await create_user()
    assert user.name == 'Robert'

    updated = await User.prisma().update(
        data={
            'name': 'Tegan',
        },
        where={
            'id': user.id,
        },
    )
    assert updated is not None
    assert updated.id == user.id
    assert updated.name == 'Tegan'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_upsert() -> None:
    """Upserting a record using model-based access"""
    user = await create_user()
    new = await User.prisma().upsert(
        where={
            'id': user.id,
        },
        data={
            'create': {
                'name': 'Robert',
            },
            'update': {
                'name': 'Robert 2',
            },
        },
    )
    assert new.name == 'Robert 2'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_update_many() -> None:
    """Updating many records using model-based access"""
    users = [
        await User.prisma().create({'name': 'Robert'}),
        await User.prisma().create({'name': 'Robert 2'}),
        await User.prisma().create({'name': 'Tegan'}),
    ]
    total = await User.prisma().update_many(
        where={
            'name': {
                'startswith': 'Robert',
            },
        },
        data={
            'name': 'Robert',
        },
    )
    assert total == 2

    for id_ in [users[0].id, users[1].id]:
        user = await User.prisma().find_unique(
            where={
                'id': id_,
            },
        )
        assert user is not None
        assert user.name == 'Robert'

    user = await User.prisma().find_unique(
        where={
            'id': users[2].id,
        },
    )
    assert user is not None
    assert user.name == 'Tegan'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_count() -> None:
    """Counting records using model-based access"""
    assert await User.prisma().count() == 0
    await create_user()
    assert await User.prisma().count() == 1

    total = await User.prisma().count(where={'NOT': [{'name': 'Robert'}]})
    assert total == 0


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_delete_many() -> None:
    """Deleting many records using model-based access"""
    _ = [
        await User.prisma().create({'name': 'Robert'}),
        await User.prisma().create({'name': 'Robert 2'}),
        await User.prisma().create({'name': 'Tegan'}),
    ]
    total = await User.prisma().delete_many(
        where={
            'name': 'Tegan',
        },
    )
    assert total == 1
    assert await User.prisma().count() == 2


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_query_raw(raw_queries: RawQueries) -> None:
    """Ensure results are transformed to the expected BaseModel"""
    users = [
        await User.prisma().create({'name': 'Robert'}),
        await User.prisma().create({'name': 'Tegan'}),
    ]
    results = await User.prisma().query_raw(
        raw_queries.find_user_by_id,
        users[1].id,
    )
    assert len(results) == 1
    assert results[0].name == 'Tegan'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_query_first(raw_queries: RawQueries) -> None:
    """Ensure results are transformed to the expected BaseModel"""
    users = [
        await User.prisma().create({'name': 'Robert'}),
        await User.prisma().create({'name': 'Tegan'}),
    ]
    user = await User.prisma().query_first(raw_queries.find_user_by_id_limit_1, users[1].id)
    assert user is not None
    assert user.name == 'Tegan'


class MyUser(User):
    @property
    def info(self) -> str:
        return f'{self.id}: {self.name}'


@pytest.mark.prisma
@pytest.mark.asyncio
async def test_custom_model() -> None:
    """Subclassed prisma model is returned by actions"""
    user = await MyUser.prisma().create(
        data={
            'name': 'Robert',
        },
    )
    assert user.info == f'{user.id}: Robert'
    assert isinstance(user, MyUser)
