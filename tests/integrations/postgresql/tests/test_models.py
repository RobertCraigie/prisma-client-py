import pytest
from prisma.models import User


class MyUser(User):
    @property
    def info(self) -> str:
        return f'{self.id}: {self.name}'


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
