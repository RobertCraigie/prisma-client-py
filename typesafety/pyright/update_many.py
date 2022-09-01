from prisma import Prisma


# TODO: more tests


async def main(client: Prisma) -> None:
    # case: missing args
    await client.post.update_many()  # E: Arguments missing for parameters "data", "where"

    # case: minimum required args
    await client.post.update_many(
        where={},
        data={},
    )

    # case: setting non-null field to null
    await client.post.update_many(
        where={
            'id': 'abc',
        },
        data={
            'published': None,  # E: Argument of type "dict[str, None]" cannot be assigned to parameter "data" of type "PostUpdateManyMutationInput" in function "update_many"
        },
    )

    # case: nullable field to null
    await client.post.update_many(
        where={
            'id': 'abc',
        },
        data={
            'desc': None,
        },
    )

    # case: one-one relations are not available
    await client.post.update_many(
        where={
            'id': 'abc',
        },
        data={
            'author': {  # E: Argument of type "dict[str, dict[str, dict[str, str]]]" cannot be assigned to parameter "data" of type "PostUpdateManyMutationInput" in function "update_many"
                'connect': {
                    'id': 'a',
                },
            },
        },
    )

    # case: one-many relations are not available
    await client.post.update_many(
        where={
            'id': 'abc',
        },
        data={
            'categories': {  # E: Argument of type "dict[str, dict[str, list[int]]]" cannot be assigned to parameter "data" of type "PostUpdateManyMutationInput" in function "update_many"
                'connect': [1],
            },
        },
    )
