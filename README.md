<br />

<div align="center">
    <h1>Prisma Client Python</h1>
    <p><h3 align="center">Type-safe database access for Python</h3></p>
</div>

<hr>

Prisma Client Python is an unofficial implementation of [Prisma Client JS](https://github.com/prisma/prisma-client-js) which is an **auto-generated query builder** that enables **type-safe** database access and **reduces boilerplate**. You can use it as an alternative to traditional ORMs such as SQLAlchemy, Django ORM, peewee and most database-specific tools.

## Example

See the [quickstart](docs/quickstart.md) tutorial for more information.

```py
import asyncio
from prisma.client import Client


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
    print(f'found post: {found.json(indent=2, sort_keys=True)}')

    await db.disconnect()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
```

## Contributing

We use [conventional commits](https://www.conventionalcommits.org) (also known as semantic commits) to ensure consistent and descriptive commit messages.

