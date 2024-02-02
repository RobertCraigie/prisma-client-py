# Configuration

There are two main methods for configuring Prisma Client Python:

1. Through the `[tool.prisma]` section in the [pyproject.toml](#config-options) file for your project

    Used for any configuration that needs to happen pre-generation such as changing the [location of the binaries](#binary-cache-directory).

2. Through the `generator` block in your [schema.prisma](#generator-options) file

    Used for any configuration that applies directly to the generated code such as generating a [synchronous or asynchronous](#interface) client.

## Generator Options

Options are passed to Prisma Client Python using the `generator` block in the `schema.prisma` file

For example:
```prisma
generator db {
  provider = "prisma-client-py"
  config_option = "value"
}
```
See the [official docs](https://www.prisma.io/docs/concepts/components/prisma-schema/generators) for options that are not specific to Prisma Client Python.

### Interface

See [setup](../getting_started/setup.md) for more information.

This option configures the method you will use to interface with the client.

Valid values are:

* asyncio
* sync

If `asyncio` is used then the generated client will be asynchronous and code must be ran using asyncio, e.g.

```py
user = await db.user.find_unique(where={'id': 'user_id'})
```

And if `sync` is used then the generated client will be synchronous, e.g.
```py
user = db.user.find_unique(where={'id': 'user_id'})
```

### Partial Type Generator

Custom partial models can be generated along with the prisma client, see [partial types](../getting_started/partial-types.md) for how to make use of partial types.

The script that generates the partial types can be configured using the `partial_type_generator` option which defaults to `prisma/partial_types.py`

You can pass either an absolute module import or a path.
!!! warning
    Passing a module will also import any parent packages, e.g. given `foo.bar.partials`, `foo` and `bar` will also be imported

#### Examples

```prisma
generator db {
  provider = "prisma-client-py"
  partial_type_generator = "scripts/partial_types.py"
}
```

```prisma
generator db {
  provider = "prisma-client-py"
  partial_type_generator = "scripts.partial_types"
}
```

### Recursive Type Depth

!!! warning
    Increasing the number of types generated can exponentially increase the time taken and resources used by static type checkers.

As some python static type checkers do not support recursive types, Prisma Client Python can generate recursive and psuedo-recursive types to an arbitrary depth.

This depth can be controlled with the `recursive_type_depth` option, if `-1` is given then recursive types will be generated and if a value greater than or equal to  `2` is given then psuedo-recursive types will be generated to the given depth.

#### Examples

These examples use the following `schema.prisma` models

```prisma
--8<-- "docs/src_examples/recursive-types.schema.prisma"
```

##### Default

The default for this option is 5. This allows for recursive types up to the following depth.

```py
user = await db.user.find_unique(
    where={'id': user_id},
    include={
        'profile': True,
        'posts': {
            'include': {
                'categories': {
                    'include': {
                        'posts': True
                    }
                }
            }
        },
    },
)
```

##### Recursive

If you are using a type checker that supports recursive types such as [pyright](https://github.com/microsoft/pyright),
you can generate fully recursive types which means that there is no depth restriction.

You can do this by setting `recursive_type_depth` to -1.

```prisma
generator db {
  provider = "prisma-client-py"
  recursive_type_depth = -1
}
```

##### Minimum Value

Generating a lot of types can drastically decreas the speed of static type checkers, in order to mitigate this it is possible to decrease the amount of types generated to any amount greater than 1.

```prisma
generator db {
  provider = "prisma-client-py"
  recursive_type_depth = 2
}
```

Recursive types are now only valid up to the following depth.

```py
user = await db.user.find_unique(
    where={'id': user_id},
    include={
        'profile': True,
        'posts': True,
    },
)
```

##### Increase

!!! warning
    Increasing the number of types generated can exponentially increase the time taken and resources used by static type checkers.

There is no maximum value, recursive types can be nested arbitrarily deep.

```prisma
generator db {
  provider = "prisma-client-py"
  recursive_type_depth = 8
}
```

Recursive types are now only valid up to the following depth.

```py
user = await db.user.find_unique(
    where={'id': user_id},
    include={
        'profile': True,
        'posts': {
            'include': {
                'categories': {
                    'include': {
                        'posts': {
                            'include': {
                                'categories': True
                            }
                        }
                    }
                }
            }
        },
    },
)
```

## Config Options

Options can either be passed to Prisma Client Python through the `pyproject.toml` file for your project, under the `tool.prisma` key, for example:

```toml
[tool.prisma]
# cache engine binaries in a directory relative to your project
binary_cache_dir = '.binaries'
```

Or through environment variables, e.g. `PRISMA_BINARY_CACHE_DIR`. In the case that the same option is set using both methods, the environment variable will take precedence.

### Binary Cache Directory

This option controls where the Prisma Engine and Prisma CLI binaries should be downloaded to. This defaults to a cache directory that includes the current Prisma Engine version.

| Option             | Environment Variable       | Default                                                                   |
| ------------------ | -------------------------- | ------------------------------------------------------------------------- |
| `binary_cache_dir` | `PRISMA_BINARY_CACHE_DIR`  | `/{home}/.cache/prisma-python/binaries/{prisma_version}/{engine_version}` |

### Home Directory

This option can be used to change the base directory of the `binary_cache_dir` option without having to worry about versioning the Prisma binaries. This is useful if you need to download the binaries to a local directory.

| Option     | Environment Variable  | Default |
| --------   | --------------------- | ------- |
| `home_dir` | `PRISMA_HOME_DIR`     | `~`     |


### Prisma Version

This option controls the version of Prisma to use. It should be noted that this is intended to be internal and only the pinned Prisma version is guaranteed to be supported.

| Option           | Environment Variable  | Default  |
| ---------------- | --------------------- | -------- |
| `prisma_version` | `PRISMA_VERSION`      | `5.9.1` |

### Expected Engine Version

This is an internal option that is here as a safeguard for the `prisma_version` option. If you modify the `prisma_version` option then you must also update this option to use the corresponding engine version. You can find a list of engine versions [here](https://github.com/prisma/prisma-engines).

| Option                    | Environment Variable             | Default                                    |
| ------------------------- | -------------------------------- | ------------------------------------------ |
| `expected_engine_version` | `PRISMA_EXPECTED_ENGINE_VERSION` | `23fdc5965b1e05fc54e5f26ed3de66776b93de64` |


### Binary Platform

This option is useful if you need to make use of the [binaryTargets](https://www.prisma.io/docs/concepts/components/prisma-schema/generators#binary-targets) schema option to build your application on one platform and deploy it on another.

This allows you to set the current platform dynamically as Prisma Client Python does not have official support for `binaryTargets` and although we do have some safe guards in place to attempt to use the correct binary, it has not been thoroughly tested.

A list of valid options can be found [here](https://www.prisma.io/docs/reference/api-reference/prisma-schema-reference#binarytargets-options).


| Option            | Environment Variable     |
| ----------------- | ------------------------ |
| `binary_platform` | `PRISMA_BINARY_PLATFORM` |

### Use Global Node

This option configures whether or not Prisma Client Python will attempt to use the globally installed version of [Node](https://nodejs.org/en/), if it is available, to run the Prisma CLI.

| Option            | Environment Variable     | Default |
| ----------------- | ------------------------ | ------- |
| `use_global_node` | `PRISMA_USE_GLOBAL_NODE` | `True`  |

### Use nodejs-bin

This option configures whether or not Prisma Client Python will attempt to use the installed version of the [nodejs-bin](https://pypi.org/project/nodejs-bin/) package, if it is available, to run the Prisma CLI.

| Option           | Environment Variable    | Default |
| ---------------- | ----------------------- | ------- |
| `use_nodejs_bin` | `PRISMA_USE_NODEJS_BIN` | `True`  |

### Extra Nodeenv Arguments

This option allows you to pass additional arguments to [nodeenv](https://github.com/ekalinin/nodeenv) which is the package we use to automatically download a Node binary to run the CLI with.

Arguments are passed after the path, for example:

```
python -m nodeenv <path> <extra args>
```

| Option               | Environment Variable        |
| -------------------- | --------------------------- |
| `nodeenv_extra_args` | `PRISMA_NODEENV_EXTRA_ARGS` |

### Nodeenv Cache Directory

This option configures where Prisma Client Python will store the Node binary that is installed by [nodeenv](https://github.com/ekalinin/nodeenv).

Note that this does not make use of the [Home Directory](#home-directory) option and instead uses the actual user home directory.

| Option              | Environment Variable       | Default                           |
| ------------------- | -------------------------- | --------------------------------- |
| `nodeenv_cache_dir` | `PRISMA_NODEENV_CACHE_DIR` | `~/.cache/prisma-python/nodeenv/` |
