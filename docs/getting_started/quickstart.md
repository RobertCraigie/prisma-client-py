# Quickstart

!!! note
    Adapted from the Prisma Client Go [documentation](https://github.com/prisma/prisma-client-go/blob/master/docs/quickstart.md)

In this page, you will learn how to send queries to an SQLite database using Prisma Client Python and
run static type checks.

## Setup

1) Setup a Python project with a [virtual environment](https://docs.python.org/3/library/venv.html)

```sh
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

<!-- TODO: show how to setup a synchronous as well and explain the difference -->

```sh
pip install prisma
```

4) Prepare your database schema in a `schema.prisma` file.

For example, a simple schema with an sqlite database and one model would look like this:

```prisma
--8<-- "docs/src_examples/async/index.schema.prisma"
```

To get this up and running in your database, we use the Prisma migration
tool [`db push`](https://www.prisma.io/docs/reference/api-reference/command-reference#db-push)
to create and migrate our database:

```sh
prisma db push
```

If you make changes to your prisma schema, you need to run this command again.

!!! note
    The `db push` command also generates the client for you, if you want to generate the client without
    modifying your database, use the following command

    ```sh
    prisma generate
    ```

!!! hint
    you can add the `--watch` flag to re-generate the client whenever you modify the `schema.prisma` file
    ```sh
    prisma generate --watch
    ```

## Usage

Create a file `main.py`:

```py
--8<-- "docs/src_examples/async/index.py"
```

and run it:

```sh
python main.py
```

```
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
```

## Static type checking

### Setup

!!! note
    I am the maintainer of the [pyright PyPI package](https://pypi.org/project/pyright/) which is a wrapper over the [official version](https://github.com/microsoft/pyright) which is maintained by microsoft

1) Install pyright

```sh
pip install pyright
```

2) Create a `pyproject.toml` file

```toml
[tool.pyright]
include = [
    "main.py",
]

typeCheckingMode = "strict"
```

### Usage

```sh
pyright
```
```
Found 1 source file
0 errors, 0 warnings, 0 infos
Completed in 1.322sec
```

### Error reporting

For example, add the following line to the end of the main() function

```py
async def main() -> None:
    ...
    print(f'Invalid field: {post.invalid_field}')
```

Running pyright will now output errors

```sh
pyright
```
```
Found 1 source file
/prisma-py-quickstart/main.py
  /prisma-py-quickstart/main.py:22:34 - error: Cannot access member "invalid_field" for type "Post"
    Member "invalid_field" is unknown (reportGeneralTypeIssues)
  /prisma-py-quickstart/main.py:22:29 - error: Type of "invalid_field" is unknown (reportUnknownMemberType)
2 errors, 0 warnings, 0 infos
Completed in 1.947sec
```

Pyright will also error whenever you try to query by a non-existent field, for example

```py
async def main() -> None:
    ...
    found = await db.post.find_unique(where={'unknown_field': post.id})
    ...
```

```sh
pyright
```
```
Found 1 source file
/prisma-py-quickstart/main.py
  /programming/prisma-py-quickstart/main.py:22:45 - error: Argument of type "dict[str, str]" cannot be assigned to parameter "where" of type "PostWhereUniqueInput" in function "find_unique"
    "unknown_field" is an undefined field in type "PostWhereUniqueInput" (reportGeneralTypeIssues)
1 error, 0 warnings, 0 infos
Completed in 1.884sec
```


## Next steps

We just scratched the surface of what you can do. Read our [advanced tutorial](advanced.md) to learn about more
complex queries and how you can query for relations.
