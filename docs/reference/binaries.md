# Binaries

Prisma Client Python interfaces with Prisma by downloading and running Rust and Node binaries. The source code for the Rust Binaries can be found [here](https://github.com/prisma/prisma-engines).

## Manual Compilation

Prisma Client Python _should_ automatically download the correct binaries for your platform, however not all platforms / architectures are supported, in this case it is possible to build the binaries yourself by following the steps outlined below.

- Clone the prisma-engines repository at the current version that the python client supports:

```
git clone https://github.com/prisma/prisma-engines --branch=4.10.1
```

- Build the binaries following the steps found [here](https://github.com/prisma/prisma-engines#building-prisma-engines)
- Make sure all 4 binaries are executable using `chmod +x <binary path>`
- Set the following environment variables:

```
PRISMA_QUERY_ENGINE_BINARY=/path/to/query-engine
PRISMA_MIGRATION_ENGINE_BINARY=/path/to/migration-engine
PRISMA_INTROSPECTION_ENGINE_BINARY=/path/to/introspection-engine
PRISMA_FMT_BINARY=/path/to/prisma-fmt
```
