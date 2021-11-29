# Setup

As Prisma Client Python supports generating both async and non-async clients, there is some differences required when generating the client.

## Installing

Prisma Client Python can be installed from [PyPi](https://pypi.org/project/prisma/) with [pip](https://pip.pypa.io/en/stable/)

```sh
pip install prisma
```

## Asyncio

### Schema

```prisma
generator client {
  provider  = "prisma-client-py"
  interface = "asyncio"
}
```

### Boilerplate

The minimum code required to get starting using asyncio:

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

### Schema

```prisma
generator client {
  provider  = "prisma-client-py"
  interface = "sync"
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
