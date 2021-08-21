<br />

<div align="center">
    <h1>Prisma Client Python</h1>
    <p><h3 align="center">Type-safe database access for Python</h3></p>
</div>

<hr>

Prisma Client Python is an unofficial implementation of [Prisma Client JS](https://github.com/prisma/prisma-client-js) which is an **auto-generated query builder** that enables **type-safe** database access and **reduces boilerplate**. You can use it as an alternative to traditional ORMs such as SQLAlchemy, Django ORM, peewee and most database-specific tools. You can also use it in either an synchronous or an asynchronous context.

It's recommended to read the official [prisma docs](https://prisma.io/docs) for all tooling around the Python client, like the [prisma schema file](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-schema/prisma-schema-file) or [prisma migrate](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-migrate).

You can try out Prisma Client Python online on [gitpod](https://gitpod.io/#https://github.com/RobertCraigie/prisma-py-async-quickstart).

## Install

See [this](docs/install.md) for installation instructions.

## Asynchronous Example

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
    assert found is not None
    print(f'found post: {found.json(indent=2, sort_keys=True)}')

    await db.disconnect()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
```
```prisma
// schema.prisma

datasource db {
    // could be postgresql or mysql
    provider = "sqlite"
    url      = "file:dev.db"
}

generator db {
    provider = "prisma-client-py"
    http     = "aiohttp"
}

model Post {
    id         String   @default(cuid()) @id
    created_at DateTime @default(now())
    updated_at DateTime @updatedAt
    title      String
    published  Boolean
    desc       String?
}
```

## Synchronous Example

```py
from prisma.client import Client

def main() -> None:
    db = Client()
    db.connect()

    post = db.post.create(
        {
            'title': 'Hello from prisma!',
            'desc': 'Prisma is a database toolkit and makes databases easy.',
            'published': True,
        }
    )
    print(f'created post: {post.json(indent=2, sort_keys=True)}')

    found = db.post.find_unique(where={'id': post.id})
    assert found is not None
    print(f'found post: {found.json(indent=2, sort_keys=True)}')

    db.disconnect()


if __name__ == '__main__':
    main()
```
```prisma
// schema.prisma

datasource db {
    // could be postgresql or mysql
    provider = "sqlite"
    url      = "file:dev.db"
}

generator db {
    provider = "prisma-client-py"
    http     = "requests"
}

model Post {
    id         String   @default(cuid()) @id
    created_at DateTime @default(now())
    updated_at DateTime @updatedAt
    title      String
    published  Boolean
    desc       String?
}
```

## Contributing

We use [conventional commits](https://www.conventionalcommits.org) (also known as semantic commits) to ensure consistent and descriptive commit messages.
