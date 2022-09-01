from prisma import Prisma


async def main(client: Prisma) -> None:
    # case: missing arguments
    await client.post.create()  # E: Argument missing for parameter "data"
    await client.post.create(
        data={}  # E: Argument of type "dict[Any, Any]" cannot be assigned to parameter "data" of type "PostCreateInput" in function "create"
    )
    await client.post.create(
        data={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "data" of type "PostCreateInput" in function "create"
            'title': '',
        },
    )

    # case: minimum required args
    await client.post.create(
        data={
            'title': '',
            'published': False,
        },
    )

    # case: nullable field to null
    await client.post.create(
        data={
            'title': 'foo',
            'published': False,
            'desc': None,
        },
    )

    # case: setting non-null field to null
    await client.post.create(
        data={
            'title': 'foo',
            'published': None,  # E: Argument of type "dict[str, str | None]" cannot be assigned to parameter "data" of type "PostCreateInput" in function "create"
        }
    )

    # case: one-one relations are non nullable
    await client.post.create(
        data={
            'title': 'foo',
            'published': False,
            'author': None,  # E: Argument of type "dict[str, str | bool | None]" cannot be assigned to parameter "data" of type "PostCreateInput" in function "create"
        },
    )
    await client.post.create(
        data={
            'title': 'foo',
            'published': False,
            'author': {
                'create': None,  # E: Argument of type "dict[str, str | bool | dict[str, None]]" cannot be assigned to parameter "data" of type "PostCreateInput" in function "create"
            },
        }
    )
    await client.post.create(
        data={
            'title': 'foo',
            'published': False,
            'author': {
                'connect': None,  # E: Argument of type "dict[str, str | bool | dict[str, None]]" cannot be assigned to parameter "data" of type "PostCreateInput" in function "create"
            },
        }
    )

    # case: one-many relations are non nullable
    await client.post.create(
        data={
            'title': 'foo',
            'published': False,
            'categories': None,  # E: Argument of type "dict[str, str | bool | None]" cannot be assigned to parameter "data" of type "PostCreateInput" in function "create"
        },
    )


async def nested_create(client: Prisma) -> None:
    # TODO: test invalid cases
    # case: valid nested create one-one
    await client.post.create(
        data={
            'title': '',
            'published': False,
            'author': {
                'create': {
                    'name': 'Robert',
                },
            },
        },
    )
    await client.post.create(
        data={
            'title': '',
            'published': False,
            'author': {
                'connect': {'id': 'a'},
            },
        },
    )

    # case: valid nested create one-many
    await client.post.create(
        data={
            'title': '',
            'published': False,
            'categories': {
                'create': {
                    'name': 'Category',
                },
            },
        },
    )
    await client.post.create(
        data={
            'title': '',
            'published': False,
            'categories': {
                'create': [
                    {
                        'name': 'Category',
                    },
                    {
                        'name': 'Category 2',
                    },
                ],
            },
        },
    )
    await client.post.create(
        data={
            'title': '',
            'published': False,
            'categories': {
                'connect': {'id': 1},
            },
        },
    )
    await client.post.create(
        data={
            'title': '',
            'published': False,
            'categories': {
                'connect': [
                    {
                        'id': 1,
                    },
                    {
                        'id': 2,
                    },
                ],
            },
        },
    )
