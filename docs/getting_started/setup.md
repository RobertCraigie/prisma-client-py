# Setup

As Prisma Client Python supports generating both async and non-async clients, there is some differences required when generating the conn.

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
from prisma import Prisma

async def main() -> None:
    conn = Prisma()
    await conn.connect()

    # write your queries here

    await conn.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
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
from prisma import Prisma

def main() -> None:
    conn = Prisma()
    conn.connect()

    # write your queries here

    conn.disconnect()

if __name__ == '__main__':
    main()
```
