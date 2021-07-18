# Configuration

Options are passed to Prisma Client Python using the `generator` block in the `schema.prisma` file

For example:
```
...
generator db {
    provider = "python -m prisma"
    config_option = "value"
}
...
```
See the [official docs](https://www.prisma.io/docs/concepts/components/prisma-schema/generators) for options that are not specific to Prisma Client Python.

# Contents

* [HTTP Libraries](#http-libraries)
* [Partial Type Generator](#partial-type-generator)
* [Model Field Transformation](#model-field-transformation)
* [Recursive Type Depth](#recursive-type-depth)

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

Custom partial models can be generated along with the prisma client, see [partial types](partial-types.md) for more information.

The script that generates the partial types can be configured using the `partial_type_generator` option (also aliased to `partialTypeGenerator`).
Defaults to `.prisma/partials.py`

You can pass either an absolute module import or a path.
> ⚠️ Passing a module will also import any parent packages, e.g. given `foo.bar.partials`, `foo` and `bar` will also be imported

### Examples

```
...
generator db {
    provider = "python -m prisma"
    partial_type_generator = "scripts/partial_types.py"
}
...
```

```
...
generator db {
    provider = "python -m prisma"
    partial_type_generator = "scripts.partial_types"
}
...
```

## Recursive Type Depth

> ⚠️ Increasing the number of types generated will exponentially increase the time taken and resources used by static type checkers.

As some python static type checkers do not support recursive types, Prisma Client Python can generate recursive and psuedo-recursive types to an arbitrary depth.

This depth can be controlled with the `recursive_type_depth` option, if `-1` is given then recursive types will be generated and if a value greater than or equal to  `2` is given then psuedo-recursive types will be generated to the given depth.

A `ValidationError` will be raised during client generation if a non-integer value or a value less than 2 is passed.

### Examples

These examples use the following `schema.prisma` models

```
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

#### Minimum Value

Generating a lot of types drastically decreases the speed of static type checkers, in order to mitigate this it is possible to decrease the amount of types generated to any amount greater than 1.

```
...
generator db {
    provider = "python -m prisma"
    recursive_type_depth = 2
}
...
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

### Increase

> ⚠️ Increasing the number of types generated will exponentially increase the time taken and resources used by static type checkers.

There is no maximum value, recursive types can be nested arbitrarily deep.

```
...
generator db {
    provider = "python -m prisma"
    recursive_type_depth = 8
}
...
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
