from prisma import Client


# TODO: more tests


async def main(client: Client) -> None:
    # case: missing args
    await client.post.update()  # E: Arguments missing for parameters "data", "where"

    # case: minimum required args
    await client.post.update(
        where={
            'id': 'foo',
        },
        data={},
    )

    # case: setting non-null field to null
    await client.post.update(
        where={
            'id': 'abc',
        },
        data={  # E: Argument of type "dict[str, None]" cannot be assigned to parameter "data" of type "PostUpdateInput" in function "update"
            'published': None,
        },
    )

    # case: nullable field to null
    await client.post.update(
        where={
            'id': 'abc',
        },
        data={
            'desc': None,
        },
    )

    # case: one-one relations are non nullable
    await client.post.update(
        where={
            'id': 'abc',
        },
        data={  # E: Argument of type "dict[str, None]" cannot be assigned to parameter "data" of type "PostUpdateInput" in function "update"
            'author': None
        },
    )

    # case: one-many relations are non nullable
    await client.post.update(
        where={
            'id': 'abc',
        },
        data={  # E: Argument of type "dict[str, None]" cannot be assigned to parameter "data" of type "PostUpdateInput" in function "update"
            'categories': None
        },
    )
