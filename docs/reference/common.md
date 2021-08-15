# Common Operations

In lieu of more extensive documentation, this page documents common operations on the prisma client such as
creating, finding, updating and deleting records.

## Schema

The examples use the following prisma schema models:
```prisma
--8<-- "docs/src_examples/common.schema.prisma"
```

## Creating

### Single Record

```py
user = await client.user.create(
    data={
        'name': 'Robert',
    },
)
```

### Many Records

!!! warning
    `create_many` is not available for SQLite

```py
users = await client.user.create_many(
    data=[
        {'name': 'Tegan'},
        {'name': 'Alfie'},
        {'name': 'Robert'},
    ]
)
```
```py
users = await client.user.create_many(
    data=[
        {'id': 'abc', 'name': 'Tegan'},
        {'id': 'def', 'name': 'Alfie'},
        {'id': 'ghi', 'name': 'Robert'},
    ],
    skip_duplicates=True,
)
```

### Relational Records

```py
user = await client.user.create(
    data={
        'name': 'Robert',
        'profile': {
            'create': {
                'bio': 'My very cool bio!',
            }
        }
    }
)
```
```py
user = await client.user.create(
    data={
        'name': 'Robert',
        'posts': {
            'create': [
                {
                    'title': 'My first post!',
                    'published': True,
                },
                {
                    'title': 'My draft post!',
                    'published': False,
                },
            ]
        }
    }
)
```

## Finding

### Unique Records

```py
user = await client.user.find_unique(
    where={
        'id': '1',
    }
)
```
```py
user = await client.user.find_unique(
    where={
        'id': '2',
    },
    include={
        'posts': True,
    },
)
```

### A Single Record

```py
post = await client.post.find_first(
    where={
        'title': {'contains': 'Post'},
    },
)
```
```py
post = await client.post.find_first(
    skip=2,
    where={
        'title': {
            'contains': 'Post'
        },
    },
    cursor={
        'id': 'abcd',
    },
    include={
        'author': True,
    },
    order={
        'id': 'asc',
    }
)
```

### Multiple Records

```py
posts = await client.post.find_many(
    where={
        'published': True,
    },
)
```
```py
posts = await client.post.find_many(
    take=5,
    skip=1,
    where={
        'published': True,
    },
    cursor={
        'id': 'desc',
    },
    include={
        'categories': True,
    },
    order={
        'id': 'desc',
    }
)
```

## Deleting

### Unique Record

```py
post = await client.post.delete(
    where={
        'id': 'cksc9m7un0028f08zwycxtjr1',
    },
)
```
```py
post = await client.post.delete(
    where={
        'id': 'cksc9m1vu0021f08zq0066pnz',
    },
    include={
        'categories': True,
    }
)
```

### Multiple Records

```py
total = await client.post.delete_many(
    where={
        'published': False,
    }
)
```

## Updating

### Unique Record

```py
post = await client.post.update(
    where={
        'id': 'cksc9lp7w0014f08zdkz0mdnn',
    },
    data={
        'views': {
            'increment': 1,
        }
    },
    include={
        'categories': True,
    }
)
```

### Multiple Records

```py
total = await client.post.update_many(
    where={
        'published': False
    },
    data={
        'views': 0,
    },
)
```

### Creating On Not Found

```py
post = await client.post.upsert(
    where={
        'id': 'cksc9ld4z0007f08z7obo806s',
    },
    data={
        'create': {
            'title': 'This post was created!',
            'published': False,
        }
        'update': {
            'title': 'This post was updated',
            'published': True,
        },
    },
    include={
        'categories': True,
    }
)
```

## Aggregrating

### Counting Records

```py
total = await client.post.count(
    where={
        'published': True,
    },
)
```
```py
total = await client.post.count(
    take=10,
    skip=1,
    where={
        'published': True,
    },
    cursor={
        'id': 'cksca3xm80035f08zjonuubik',
    },
    order={
        'created_at': 'asc',
    },
)
```

## Batching Write Queries

```py
async with client.batch_() as batcher:
    batcher.user.create({'name': 'Robert'})
    batcher.user.create({'name': 'Tegan'})
```

## Raw Queries

!!! note
    SQL queries are sent directly to the database so you must use the syntax for your specific database provider

!!! warning
    Raw query results are raw dictionaries unless the `model` argument is specified

### Write Queries

```py
total = await client.execute_raw(
    '''
    SELECT *
    FROM User
    WHERE User.id = ?
    ''',
    'cksca3xm80035f08zjonuubik'
)
```

### Selecting Multiple Records

```py
posts = await client.query_raw(
    '''
    SELECT *
    FROM Post
    WHERE Post.published IS TRUE
    '''
)
```

#### Type Safety

```py
from prisma.models import Post

posts = await client.query_raw(
    '''
    SELECT *
    FROM Post
    WHERE Post.published IS TRUE
    ''',
    model=Post,
)
```

### Selecting a Single Record

```py
post = await client.query_first(
    '''
    SELECT *
    FROM Post
    WHERE Post.published IS TRUE
    LIMIT 1
    '''
)
```

#### Type Safety

```py
from prisma.models import Post

post = await client.query_first(
    '''
    SELECT *
    FROM Post
    WHERE Post.views > 50
    LIMIT 1
    ''',
    model=Post
)
```
