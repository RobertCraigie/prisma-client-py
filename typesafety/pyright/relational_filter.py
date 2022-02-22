from prisma import Prisma


async def one_to_one_relation(client: Prisma) -> None:
    """Ensure relational filters are strongly typed with pyright"""
    user = await client.user.find_first(
        where={
            'profile': {
                'is': {
                    'bio': {'contains': 'scotland'},
                },
            },
        }
    )
    assert user is not None
    reveal_type(user)  # T: User
    reveal_type(user.id)  # T: str
    reveal_type(user.profile)  # T: Profile | None

    await client.user.find_first(
        where={  # E: Argument of type "dict[str, dict[str, dict[str, str]]]" cannot be assigned to parameter "where" of type "UserWhereInput | None" in function "find_first"
            'profile': {
                'is': {
                    'an_invalid_value': 'foo',
                },
            },
        },
    )
