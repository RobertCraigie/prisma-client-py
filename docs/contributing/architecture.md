# Architecture

<!-- TODO: more detail -->

This page covers how core Prisma Client Python features work internally. It's intended to aid in inderstanding the code and hopefully enabling more people to contribute.

!!! note
    This page assumes you have at least a basic working knowledge of python.

## Design Principles

* **Type Safety**

    Every python API operation *must* have accurate type definitions.

## Overview

<!-- TODO: mermaid.js diagrams -->

Prisma Client Python is made up of two core components, [Client generation](#generation) and the [Client API](#client-api).

### Generation

Parsing schema files and invoking generators is handled internally by Prisma.

Behind the scenes, the provider value is simply a pointer to a shell script, for example, the following generators are all functionally equivalent.

```prisma
generator client {
  provider = "prisma-client-py"
}
```
```prisma
generator client {
  provider = "python3 -m prisma"
}
```
```prisma
generator client {
  provider = "python3 -c 'from prisma.cli import main; main()'"
}
```

#### How Does it Work?

Prisma sends data to generators using [JSON-RPC](https://www.jsonrpc.org/specification), our implementation can be found at `src/prisma/generator/jsonrpc.py` and the communication with Prisma is implemented in the `BaseGenerator.invoke()` function in `src/prisma/generator/generator.py`

Control flow:

- `prisma generate`
- Prisma starts generator process
- Generator process waits for message from prisma
- Prisma sends `getManifest` for generator metadata
- Generator responds and waits for a new message
- Prisma sends `generate`
- Generator writes the python files to disk and sends empty response
- Prisma closes the generator process

When the `generate` message is sent, prisma includes a DMMF which is the Prisma Schema AST which represents the Prisma Schema File in JSON form.

We then parse the DMMF into pydantic [models](https://docs.pydantic.dev/latest/usage/models/), this ensures our code is expecting the same DMMF structure that prisma is providing. The DMMF models can be found in `src/prisma/generator/models.py`.

We then use [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/) to render the python files and then write them to the output location.


### Client API

In short, the Client API is a wrapper over the GraphQL API exposed by the Prisma Query Engine.

### How Does it Work?

#### Connecting

When `Client.connect()` is called the following steps are taken:

- Find the query engine binary
- Start the query engine process
- Send health checks to the HTTP API until the server is ready

#### Executing queries

Queries are executed by sending a GraphQL request to the query engine server, queries are built by the rendered `builder.py` file which corresponds to the `src/prisma/generator/templates/builder.py.jinja` template.

Queries look something like this:

```graphql
query {
  result: findUniqueUser
  (
    where: {
      id: "ckq23ky3003510r8zll5m2hma"
    }
  )
  {
    id
    name
    profile {
      id
      user_id
      bio
    }
  }
}
```

Database operations are handled by Prisma's query engine binary, see this graph from the prisma documentation.

![client diagram](https://res.cloudinary.com/prismaio/image/upload/v1628764928/docs/I8do25A_ynswyd.png)
