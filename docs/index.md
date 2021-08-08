<br />

<div align="center">
    <h1>Prisma Client Python</h1>
    <p><h3 align="center">Type-safe database access for Python</h3></p>
</div>

<hr>

Prisma Client Python is an unofficial implementation of [Prisma Client JS](https://github.com/prisma/prisma-client-js) which is an **auto-generated query builder** that enables **type-safe** database access and **reduces boilerplate**. You can use it as an alternative to traditional ORMs such as SQLAlchemy, Django ORM, peewee and most database-specific tools. You can also use it in either an synchronous or an asynchronous context.

It's recommended to read the official [prisma docs](https://prisma.io/docs) for all tooling around the Python client, like the [prisma schema file](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-schema/prisma-schema-file) or [prisma migrate](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-migrate).

## Install

See [here](install.md) for installation instructions.

## Example

See the [quickstart](quickstart.md) tutorial for more information.

=== "Asynchronous"
    ```py
    --8<-- "docs/src_examples/async/index.py"
    ```
    `schema.prisma`
    ```prisma
    --8<-- "docs/src_examples/async/index.schema.prisma"
    ```

=== "Synchronous"
    ```py
    --8<-- "docs/src_examples/sync/index.py"
    ```
    `schema.prisma`
    ```prisma
    --8<-- "docs/src_examples/sync/index.schema.prisma"
    ```
