from prisma.models import User


class MyUser(User):
    @property
    def hello(self):
        return f'Hello, {self.name}!'


async def create() -> None:
    # case: valid
    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
    )
    reveal_type(user)  # T: User

    user = await User.prisma().create(
        data={
            'name': 'Robert',
            'profile': {
                'create': {
                    'bio': 'hello',
                },
            },
        },
    )
    reveal_type(user)  # T: User

    # case: pyright overloading
    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
    )
    reveal_type(user)  # T: User

    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
        include={},
    )
    reveal_type(user)  # T: User

    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
        include={},
        discard_result=False,
    )
    reveal_type(user)  # T: User

    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
        discard_result=False,
    )
    reveal_type(user)  # T: User

    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
        include={},
        discard_result=True,
    )
    reveal_type(user)  # T: None

    user = await User.prisma().create(
        data={
            'name': 'Robert',
        },
        discard_result=True,
    )
    reveal_type(user)  # T: None

    # case: subclassing
    user2 = await MyUser.prisma().create(
        data={
            'name': 'Robert',
        },
    )
    reveal_type(user2)  # T: MyUser
    reveal_type(user2.hello)  # T: str

    # case: invalid field
    await User.prisma().create(
        data={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "data" of type "UserCreateInput" in function "create"
            'foo': 'Robert',
        },
    )

    # case: invalid nested field
    await User.prisma().create(
        data={  # E: Argument of type "dict[str, str | dict[str, dict[str, str]]]" cannot be assigned to parameter "data" of type "UserCreateInput" in function "create"
            'name': 'Robert',
            'profile': {
                'create': {
                    'foo': 'bar',
                },
            },
        },
    )
