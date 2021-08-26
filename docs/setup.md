# Setup

As Prisma Client Python supports generating both async and non-async clients, there is some differences required when installing and configuring the client.

For example you must specify the http library that the client will use to communicate with the internal [query engine](https://www.prisma.io/docs/concepts/overview/under-the-hood#prisma-engines).

## Asynchronous client

Currently supported HTTP libraries are:

* [aiohttp](https://github.com/aio-libs/aiohttp)

### Installing

```sh
pip install prisma-client[aiohttp]
```

### Schema

```prisma
generator client {
  provider = "prisma-client-py"
  http     = "aiohttp"
}
```

### Boilerplate

The minimum code required to get starting using an asynchronous client:

```py
import asyncio
from prisma import Client

async def main() -> None:
    client = Client()
    await client.connect()

    # write your queries here

    await client.disconnect()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
```

## Synchronous client

Currently supported HTTP libraries are:

* [requests](https://github.com/psf/requests)

### Installing

```sh
pip install prisma-client[requests]
```

### Schema

```prisma
generator client {
  provider = "prisma-client-py"
  http     = "requests"
}
```

### Boilerplate

The minimum code required to get starting using a synchronous client:

```py
from prisma import Client

def main() -> None:
    client = Client()
    client.connect()

    # write your queries here

    client.disconnect()

if __name__ == '__main__':
    main()
```
