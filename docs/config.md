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

## Model Field Transformation

> [@map](https://www.prisma.io/docs/reference/api-reference/prisma-schema-reference#map) can be used to transform individual field names

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
