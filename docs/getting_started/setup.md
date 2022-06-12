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
  provider             = "prisma-client-py"
  interface            = "asyncio"
  recursive_type_depth = 5
}
```

### Boilerplate

The minimum code required to get starting using asyncio:

```py
import asyncio
from prisma import Prisma

async def main() -> None:
    db = Prisma()
    await db.connect()

    # write your queries here

    await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
```

## Synchronous client

### Schema

```prisma
generator client {
  provider             = "prisma-client-py"
  interface            = "sync"
  recursive_type_depth = 5
}
```

### Boilerplate

The minimum code required to get starting using a synchronous client:

```py
from prisma import Prisma

def main() -> None:
    db = Prisma()
    db.connect()

    # write your queries here

    db.disconnect()

if __name__ == '__main__':
    main()
```
