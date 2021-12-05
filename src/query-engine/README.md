# Rust Query Engine Bindings

This package contains the Python to Rust bindings for the Prisma Query Engine.

The vast majority of this code has been copied from https://github.com/prisma/prisma-engines/tree/master/query-engine/query-engine-node-api and modified to replace the [N-API](https://github.com/napi-rs/napi-rs) bindings with [PyO3](https://github.com/prisma/prisma-engines/tree/master/query-engine/query-engine-node-api) bindings.

The only completely original code is `src/py_api.rs`

## Usage

This package is not intended for public use and is only published separately from [prisma](https://pypi.org/project/prisma/) so that it can remain an optional dependency until it is stable.
