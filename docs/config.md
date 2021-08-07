# Configuration

Options are passed to Prisma Client Python using the `generator` block in the `schema.prisma` file

For example:
```prisma
generator db {
    provider = "prisma-client-py"
    config_option = "value"
}
```
See the [official docs](https://www.prisma.io/docs/concepts/components/prisma-schema/generators) for options that are not specific to Prisma Client Python.

## HTTP Libraries

See [install](install.md) for more information.

The HTTP library that will be used by Prisma Client Python can be configured using the `http` option.

Valid values are:

* aiohttp
* requests

If aiohttp is used then the generated client will be asynchronous, e.g.
```py
user = await client.user.find_unique(where={'id': 'user_id'})
```

And if requests is used then the generated client will be synchronous, e.g.
```py
user = client.user.find_unique(where={'id': 'user_id'})
```

## Partial Type Generator

Custom partial models can be generated along with the prisma client, see [partial types](partial-types.md) for what this means and how to make use of them.

The script that generates the partial types can be configured using the `partial_type_generator` option which defaults to `prisma/partial_types.py`

You can pass either an absolute module import or a path.
!!! warning
    Passing a module will also import any parent packages, e.g. given `foo.bar.partials`, `foo` and `bar` will also be imported

### Examples

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

## Recursive Type Depth

!!! warning
    Increasing the number of types generated can exponentially increase the time taken and resources used by static type checkers.

As some python static type checkers do not support recursive types, Prisma Client Python can generate recursive and psuedo-recursive types to an arbitrary depth.

This depth can be controlled with the `recursive_type_depth` option, if `-1` is given then recursive types will be generated and if a value greater than or equal to  `2` is given then psuedo-recursive types will be generated to the given depth.

### Examples

These examples use the following `schema.prisma` models

```prisma
model Post {
    id         String      @default(cuid()) @id
    title      String
    author     User?       @relation(fields:  [author_id], references: [id])
    author_id  String?
    categories Category[]  @relation(references: [id])
}

model User {
    id        String   @default(cuid()) @id
    name      String
    posts     Post[]
    profile   Profile?
}

model Category {
    id    Int    @id @default(autoincrement())
    posts Post[] @relation(references: [id])
    name  String
}

model Profile {
  id      Int    @id @default(autoincrement())
  user    User   @relation(fields:  [user_id], references: [id])
  user_id String
  bio     String
}
```

#### Default

The default for this option is 5. This allows for recursive types up to the following depth.

```py
user = await client.user.find_unique(
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

#### Recursive

If you are using a type checker that supports recursive types such as [pyright](https://github.com/microsoft/pyright),
you can generate fully recursive types which means that there is no depth restriction.

You can do this by setting `recursive_type_depth` to -1.

```prisma
generator db {
    provider = "prisma-client-py"
    recursive_type_depth = -1
}
```

#### Minimum Value

Generating a lot of types can drastically decreas the speed of static type checkers, in order to mitigate this it is possible to decrease the amount of types generated to any amount greater than 1.

```prisma
generator db {
    provider = "prisma-client-py"
    recursive_type_depth = 2
}
```

Recursive types are now only valid up to the following depth.

```py
user = await client.user.find_unique(
    where={'id': user_id},
    include={
        'profile': True,
        'posts': True,
    },
)
```

#### Increase

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
user = await client.user.find_unique(
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
