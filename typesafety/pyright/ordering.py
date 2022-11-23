from prisma import Prisma


async def order(client: Prisma) -> None:
    # case: valid
    await client.post.find_first(
        order={
            'desc': 'asc',
        },
    )
    await client.post.find_first(
        order={
            'title': 'asc',
        },
    )
    await client.post.find_first(
        order=[
            {'desc': 'asc'},
            {'title': 'asc'},
        ],
    )

    # case: one field allowed
    await client.post.find_first(
        order={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "order" of type "PostOrderByInput | List[PostOrderByInput] | None" in function "find_first"
            'desc': 'asc',
            'title': 'asc',
        },
    )
    await client.post.find_first(
        order=[
            {  # E: Argument of type "list[dict[str, str] | _Post_title_OrderByInput]" cannot be assigned to parameter "order" of type "PostOrderByInput | List[PostOrderByInput] | None" in function "find_first"
                'desc': 'asc',
                'title': 'asc',
            },
            {'title': 'asc'},
        ],
    )
