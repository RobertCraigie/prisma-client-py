from prisma import Prisma


async def main(client: Prisma) -> None:
    # data is missing create and update keys
    post = await client.post.upsert(
        where={
            'id': 'abc',
        },
        data={},  # E: Argument of type "dict[Any, Any]" cannot be assigned to parameter "data" of type "PostUpsertInput" in function "upsert"
    )

    # data is missing the update key
    post = await client.post.upsert(
        where={
            'id': 'abc',
        },
        data={  # E: Argument of type "dict[str, PostCreateInput]" cannot be assigned to parameter "data" of type "PostUpsertInput" in function "upsert"
            'create': {
                'title': 'My post',
                'published': False,
            },
        },
    )

    # create is missing required values
    post = await client.post.upsert(
        where={
            'id': 'abc',
        },
        data={  # E: Argument of type "dict[str, PostUpdateInput | dict[Any, Any]]" cannot be assigned to parameter "data" of type "PostUpsertInput" in function "upsert"
            'create': {},
            'update': {},
        },
    )

    # create is missing a required value
    post = await client.post.upsert(
        where={
            'id': 'abc',
        },
        data={  # E: Argument of type "dict[str, dict[str, str] | PostUpdateInput]" cannot be assigned to parameter "data" of type "PostUpsertInput" in function "upsert"
            'create': {'title': 'My post'},
            'update': {},
        },
    )

    # valid
    post = await client.post.upsert(
        where={
            'id': 'abc',
        },
        data={
            'create': {
                'title': 'My post',
                'published': False,
            },
            'update': {},
        },
    )
