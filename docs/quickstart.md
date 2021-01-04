# Quickstart

## Setup

1) Setup a Python project with a [virtual environment](https://docs.python.org/3/library/venv.html)

    ```shell script
    mkdir demo && cd demo
    python3 -m venv .venv
    ```


2) Activate the virtual environment

    Note that you will have to run the activation command on every new shell instance.

    | Platform | Shell           | Activation Command                      |
    | -------- | --------------- | --------------------------------------- |
    | POSIX    | bash/zsh        | `$ source .venv/bin/activate`           |
    |          | fish            | `$ source .venv/bin/activate.fish`      |
    |          | csh/tcsh        | `$ source .venv/bin/activate.csh`       |
    |          | PowerShell Core | `$ .venv/bin/Activate.ps1`              |
    | Windows  | cmd.exe         | `C:\> .venv\Scripts\activate.bat`       |
    |          | PowerShell      | `PS C:\> .venv\Scripts\Activate.ps1`    |


3) Install Prisma Client Python

    ```shell script
    pip install git+https://github.com/RobertCraigie/prisma-client-py
    ```

4) Prepare your database schema in a `schema.prisma` file.

   For example, a simple schema with an sqlite database and one model would look like this:

    ```prisma
    datasource db {
        // could be postgresql or mysql
        provider = "sqlite"
        url      = "file:dev.db"
    }

    generator db {
        provider = "python -m prisma"
    }

    model Post {
        id        String   @default(cuid()) @id
        createdAt DateTime @default(now())
        updatedAt DateTime @updatedAt
        title     String
        published Boolean
        desc      String?
    }
    ```

    To get this up and running in your database, we use the Prisma migration
    tool [`migrate`](https://github.com/prisma/migrate) (Note: this tool is experimental) to create and migrate our
    database:

     ```shell script
    # initialize the first migration
    python -m prisma migrate save --experimental --create-db --name "init"
    # apply the migration
    python -m prisma migrate up --experimental
    ```

5) Generate the Prisma Client Python client in your project

     ```shell script
    python -m prisma generate
    ```

    If you make changes to your prisma schema, you need to run this command again.

## Usage

Create a file `main.py`:

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
    print(f'post description is "{found.desc}"')

    await db.disconnect()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

```

and run it:

```shell script
python main.py
```

```
❯ python main.py
created post: {
  "created_at": "2021-01-04T00:30:35.921000+00:00",
  "desc": "Prisma is a database toolkit and makes databases easy.",
  "id": "ckjhtv79t0000y1uicwrgt605",
  "published": true,
  "title": "Hello from prisma!",
  "updated_at": "2021-01-04T00:30:35.921000+00:00"
}
found post: {
  "created_at": "2021-01-04T00:30:35.921000+00:00",
  "desc": "Prisma is a database toolkit and makes databases easy.",
  "id": "ckjhtv79t0000y1uicwrgt605",
  "published": true,
  "title": "Hello from prisma!",
  "updated_at": "2021-01-04T00:30:35.921000+00:00"
}
post description is "Prisma is a database toolkit and makes databases easy.""
```

## Setup Static Type Checking

1) Install mypy

    ```shell script
    pip install mypy
    ```

2) Create a mypy config file `mypy.ini`

    ```
    [mypy]
    strict = True
    ```

## Usage

```shell script
python -m mypy .
```

```
❯ python -m mypy .
Success: no issues found in 1 source file
```

All prisma client methods are fully statically typed, this means that mypy will output an error
if you try to access an unknown field <TODO etc>

For example, add the following line to the end of the main() function

```py
async def main() -> None:
    ...
    print(f'Invalid field: {post.invalid_field}')
```

```
❯ python -m mypy .
main.py:24: error: "Post" has no attribute "invalid_field"
Found 1 error in 1 file (checked 1 source file)
```


### Next steps

<TODO: advanced tutorial>
