import asyncio
from prisma import Client

async def main() -> None:
    db = Client()
    await db.connect()

    post = await db.post.create(
        {
            'title': 'Hello from prisma!',
            'desc': 'Prisma is a database toolkit and makes databases easy.',
            'published': True,
        }
    )
    print(f'created post: {post.json(indent=2, sort_keys=True)}')

    found = await db.post.find_unique(where={'id': post.id})
    assert found is not None
    print(f'found post: {found.json(indent=2, sort_keys=True)}')

    await db.disconnect()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
