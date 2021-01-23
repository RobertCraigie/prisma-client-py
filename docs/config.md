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

## Model Field Transformation

> [@map](https://www.prisma.io/docs/reference/api-reference/prisma-schema-reference#map) should be used to transform individual field names

As per python convention Prisma Client Python transforms model fields to `snake_case`.
This behaviour can be controlled with the `transform_fields` option (also aliased to `transformFields`).

Valid values are:

* none
* snake_case
* camelCase
* PascalCase

A `ValidationError` will be raised during client generation if an invalid value is passed.

### Examples

These examples use the following `schema.prisma` model
```
model Post {
    id          String   @default(cuid()) @id
    createdAt   DateTime @default(now())
    updated_at  DateTime @updatedAt
    Title       String
    PublishedAt Boolean
    desc        String?
}
```

#### Snake Case

```
...
generator db {
    provider = "python -m prisma"
    transform_fields = "snake_case"
}
...
```

```py
class Post:
    id: str
    title: str
    published_at
    desc: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
```

#### None

```
...
generator db {
    provider = "python -m prisma"
    transform_fields = "none"
}
...
```

```py
class Post:
    id: str
    Title: str
    PublishedAt: bool
    desc: Optional[str]
    createdAt: datetime.datetime
    updated_at: datetime.datetime
```

#### Camel Case

```
...
generator db {
    provider = "python -m prisma"
    transform_fields = "camelCase"
}
...
```

```py
class Post:
    id: str
    title: str
    publishedAt: bool
    desc: Optional[str]
    createdAt: datetime.datetime
    updatedAt: datetime.datetime
```

#### Pascal Case

```
...
generator db {
    provider = "python -m prisma"
    transform_fields = "PascalCase"
}
...
```

```py
class Post:
    Id: str
    Title: str
    PublishedAt: bool
    Desc: Optional[str]
    CreatedAt: datetime.datetime
    UpdatedAt: datetime.datetime
```

## Recursive Type Depth

> ⚠️ Increasing the number of types generated will exponentially increase the time taken and resources used by static type checkers.

As many python static type checkers do not support recursive types Prisma Client Python duplicates would-be recursive types to an arbitrary depth. This depth can be controlled with the `recursive_type_depth` option (also aliased to `recursiveTypeDepth`).

A `ValidationError` will be raised during client generation if a non-integer value or a value less than 2 is passed.

### Examples

These examples use the following `schema.prisma` models

```
model Post {
    id         String      @default(cuid()) @id
    title      String
    author     User?       @relation(fields:  [authorId], references: [id])
    authorId   String?
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
  user    User   @relation(fields:  [userId], references: [id])
  userId  String
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
