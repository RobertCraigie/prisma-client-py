from prisma import Prisma


# TODO: more tests


async def main(client: Prisma) -> None:
    # case: no arguments
    total = await client.post.count()
    reveal_type(total)  # T: int


async def select(client: Prisma) -> None:
    # case: None
    total = await client.post.count(select=None)
    reveal_type(total)  # T: int

    # case: empty
    count = await client.post.count(select={})
    reveal_type(count)  # T: PostCountAggregateOutput

    # case: valid fields
    count = await client.post.count(
        select={
            '_all': True,
            'views': True,
            'created_at': True,
            'desc': False,
        },
    )
    reveal_type(count)  # T: PostCountAggregateOutput

    # case: invalid field
    await client.post.count(
        select={  # E: Argument of type "dict[str, bool]" cannot be assigned to parameter "select" of type "PostCountAggregateInput" in function "count"
            'foo': True,
        },
    )

    # case: invalid type
    await client.post.count(
        select={  # E: Argument of type "dict[str, int]" cannot be assigned to parameter "select" of type "PostCountAggregateInput" in function "count"
            'author_id': 1,
        },
    )
