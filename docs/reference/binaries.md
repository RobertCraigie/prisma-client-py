# Binaries

Prisma Client Python interfaces with Prisma by downloading and running Rust and Node binaries. The source code for the Rust Binaries can be found [here](https://github.com/prisma/prisma-engines).

## Manual Compilation

Prisma Client Python *should* automatically download the correct binaries for your platform, however not all platforms / architectures are supported, in this case it is possible to build the binaries yourself by following the steps outlined below.

- Clone the prisma-engines repository at the current version that the python client supports:

```
git clone https://github.com/prisma/prisma-engines --branch=3.12.0
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

## CLI Compilation

Manually building the CLI binary is not fully supported yet however the basis to get this working can be found [here](https://github.com/RobertCraigie/prisma-client-py/issues/195#issuecomment-1001287195) (note that you must replace `v="3.4.0"` with the current version which can be found above).

Once you have managed to build the CLI binary you can tell Prisma Client Python to use it by setting the `PRISMA_CLI_BINARY` environment variable.
