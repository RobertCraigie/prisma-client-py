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

## HTTP Options

Some of the methods that Prisma Client Python uses to communicate with the underlying Prisma binaries make use of [HTTPX](https://github.com/encode/httpx/) to communicate over HTTP. As such, some [HTTPX Client options](https://www.python-httpx.org/api/#client) are configurable on a per-client basis, this can be especially useful in certain situations where the default timeout of 5 seconds is too little.

The HTTPX options can be passed to client using the `http` parameter, for example:

```py
client = Client(
    http={
        'timeout': 10,
    },
)
```

Will then use a 10 second timeout for all http operations.

Not all options that HTTPX support are supported by Prisma Client Python, a full list can be found below:

```py
class HttpConfig(TypedDict, total=False):
    app: Callable[[Mapping[str, Any], Any], Any]
    http1: bool
    http2: bool
    limits: httpx.Limits
    timeout: Union[float, httpx.Timeout]
    trust_env: bool
    max_redirects: int
```

The documentation behind these options can be found [here](https://www.python-httpx.org/api/#client)
