from prisma import Client


# TODO: more tests


async def main(client: Client) -> None:
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
        data={  # E: Argument of type "dict[str, None]" cannot be assigned to parameter "data" of type "PostUpdateManyMutationInput" in function "update_many"
            'published': None,
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

    # case: one-one relations are non nullable
    await client.post.update_many(
        where={
            'id': 'abc',
        },
        data={  # E: Argument of type "dict[str, None]" cannot be assigned to parameter "data" of type "PostUpdateManyMutationInput" in function "update_many"
            'author': None
        },
    )

    # case: one-many relations are non nullable
    await client.post.update_many(
        where={
            'id': 'abc',
        },
        data={  # E: Argument of type "dict[str, None]" cannot be assigned to parameter "data" of type "PostUpdateManyMutationInput" in function "update_many"
            'categories': None
        },
    )
