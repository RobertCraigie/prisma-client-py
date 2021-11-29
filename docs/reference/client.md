# Client

In order to make *any* Prisma Client Python queries you need to create and connect to a `Client` instance, for example:

```py
from prisma import Client

client = Client()
await client.connect()
await client.user.create(
    data={
        'name': 'Robert',
    },
)
```

You can also query directly from model classes, see [Model Actions](./model-actions.md) for more information.

```py
from prisma.models import User

user = await User.prisma().create(
    data={
        'name': 'Robert',
    },
)
```

## Datasource Overriding

It is possible to override the default URL used to connect to the database:

```py
client = Client(
    datasource={
        'url': 'file:./tmp.db',
    },
)
```

## Context Manager

To make running small scripts as easy as possible, Prisma Client Python supports connecting and disconnecting from the database using a [context manager](https://book.pythontips.com/en/latest/context_managers.html).

For example:

```py
from prisma import Client

async with Client() as client:
    await client.user.create(
        data={
            'name': 'Robert',
        },
    )
```

Which is functionally equivalent to:

```py
from prisma import Client

client = Client()

try:
    await client.connect()
    await client.user.create(
        data={
            'name': 'Robert',
        },
    )
finally:
    if client.is_connected():
        await client.disconnect()
```
