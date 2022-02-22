# Query Operations

In lieu of more extensive documentation, this page documents query operations on the prisma client such as
creating, finding, updating and deleting records.

## Schema

The examples use the following prisma schema models:
```prisma
--8<-- "docs/src_examples/operations.schema.prisma"
```

## Creating

### Single Record

```py
user = await db.user.create(
    data={
        'name': 'Robert',
    },
)
```

### Many Records

!!! warning
    `create_many` is not available for SQLite

```py
users = await db.user.create_many(
    data=[
        {'name': 'Tegan'},
        {'name': 'Alfie'},
        {'name': 'Robert'},
    ]
)
```
```py
users = await db.user.create_many(
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
user = await db.user.create(
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
user = await db.user.create(
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
user = await db.user.find_unique(
    where={
        'id': '1',
    }
)
```
```py
user = await db.user.find_unique(
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
post = await db.post.find_first(
    where={
        'title': {'contains': 'Post'},
    },
)
```
```py
post = await db.post.find_first(
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
posts = await db.post.find_many(
    where={
        'published': True,
    },
)
```
```py
posts = await db.post.find_many(
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

### Filtering by Relational Fields

Within the filter you can query for everything you would normally query for, like it was a `find_first()` call on the relational field, for example:

```py
post = await db.post.find_first(
    where={
        'author': {
            'is': {
                'name': 'Robert',
            },
        },
    },
)
user = await db.user.find_first(
    where={
        'name': 'Robert',
    },
)
```

#### One to One

```py
post = await db.post.find_first(
    where={
        'author': {
            'is': {
                'name': 'Robert',
            },
            'is_not': {
                'name': 'Tegan',
            },
        },
    },
)
```

#### One to Many

##### Excluding

```py
post = await db.post.find_first(
    where={
        'categories': {
            'none': {
                'name': 'Exclude Category',
            },
        },
    },
)
```

##### At Least One

```py
post = await db.post.find_first(
    where={
        'categories': {
            'some': {
                'name': {
                    'contains': 'Special',
                },
            },
        },
    },
)
```

##### Every

```py
post = await db.post.find_first(
    where={
        'categories': {
            'every': {
                'name': {
                    'contains': 'Category',
                },
            },
        },
    },
)
```

### Filtering by Field Values

!!! note
    The examples for filtering fields are simply to showcase possible arguments, all the arguments
    passed together will result in either an invalid query or no records being found.

#### String Fields

!!! warning
    Case insensitive filtering is only available on PostgreSQL and MongoDB

```py
post = await db.post.find_first(
    where={
        'description': 'Must be exact match',
        # or
        'description': {
            'equals': 'example_string',
            'not_in': ['ignore_string_1', 'ignore_string_2'],
            'lt': 'z',
            'lte': 'y',
            'gt': 'a',
            'gte': 'b',
            'contains': 'string must be present',
            'startswith': 'must start with string',
            'endswith': 'must end with string',
            'in': ['find_string_1', 'find_string_2'],
            'mode': 'insensitive',
            'not': {
                # recursive type
                'contains': 'string must not be present',
                'mode': 'default',
                ...
            },
        },
    },
)
```

#### Integer Fields

```py
post = await db.post.find_first(
    where={
        'views': 10,
        # or
        'views': {
            'equals': 1,
            'in': [1, 2, 3],
            'not_in': [4, 5, 6],
            'lt': 10,
            'lte': 9,
            'gt': 0,
            'gte': 1,
            'not': {
                # recursive type
                'gt': 10,
                ...
            },
        },
    },
)
```

#### Float Fields

```py
user = await db.user.find_first(
    where={
        'points': 10.0,
        # or
        'points': {
            'equals': 10.0,
            'in': [1.2, 1.3, 1.4],
            'not_in': [4.7, 53.4, 6.8],
            'lt': 100.5,
            'lte': 9.9,
            'gt': 0.0,
            'gte': 1.2,
            'not': {
                # recursive type
                'gt': 10.0,
                ...
            },
        },
    },
)
```

#### DateTime Fields

```py
from datetime import datetime

post = await db.post.find_first(
    where={
        'updated_at': datetime.now(),
        # or
        'updated_at': {
            'equals': datetime.now(),
            'not_in': [datetime.now(), datetime.utcnow()],
            'lt': datetime.now(),
            'lte': datetime.now(),
            'gt': datetime.now(),
            'gte': datetime.now(),
            'in': [datetime.now(), datetime.utcnow()],
            'not': {
                # recursive type
                'equals': datetime.now(),
                ...
            },
        },
    },
)
```

#### Boolean Fields

```py
post = await db.post.find_first(
    where={
        'published': True,
        # or
        'published': {
            'equals': True,
            'not': False,
        },
    },
)
```

#### Json Fields

!!! note
    Json fields must match _exactly_.

!!! warning
    Json fields are not supported on SQLite

```py
from prisma import Json

user = await db.user.find_first(
    where={
        'meta': Json({'country': 'Scotland'})
        # or
        'meta': {
            'equals': Json.keys(country='Scotland'),
            'not': Json(['foo']),
        }
    }
)
```

#### Bytes Fields

!!! note
    Bytes fields are encoded to and from [Base64](https://en.wikipedia.org/wiki/Base64)

```py
from prisma import Base64

profile = await db.profile.find_first(
    where={
        'image': Base64.encode(b'my binary data'),
        # or
        'image': {
            'equals': Base64.encode(b'my binary data'),
            'not': Base64(b'WW91IGZvdW5kIGFuIGVhc3RlciBlZ2chIExldCBAUm9iZXJ0Q3JhaWdpZSBrbm93IDop'),
        },
    },
)
```

#### Lists fields

!!! warning
    Scalar list fields are only supported on PostgreSQL and MongoDB

Every scalar type can also be defined as a list, for example:

```py
user = await db.user.find_first(
    where={
        'emails': {
            # only one of the following fields is allowed at the same time
            'has': 'robert@craigie.dev',
            'has_every': ['email1', 'email2'],
            'has_some': ['email3', 'email4'],
            'is_empty': True,
        },
    },
)
```

### Combining arguments

All of the above mentioned filters can be combined with other filters using `AND`, `NOT` and `OR`.

#### AND

The following query will return the first post where the title contains the words `prisma` and `test`.

```py
post = await db.post.find_first(
    where={
        'AND': [
            {
                'title': {
                    'contains': 'prisma',
                },
            },
            {
                'title': {
                    'contains': 'test',
                },
            },
        ],
    },
)
```

#### OR

The following query will return the first post where the title contains the word `prisma` or is published.

```py
post = await db.post.find_first(
    where={
        'OR': [
            {
                'title': {
                    'contains': 'prisma',
                },
            },
            {
                'published': True,
            },
        ],
    },
)
```

#### NOT

The following query will return the first post where the title is not `My test post`

```py
post = await db.post.find_first(
    where={
        'NOT' [
            {
                'title': 'My test post',
            },
        ],
    },
)
```

## Deleting

### Unique Record

```py
post = await db.post.delete(
    where={
        'id': 'cksc9m7un0028f08zwycxtjr1',
    },
)
```
```py
post = await db.post.delete(
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
total = await db.post.delete_many(
    where={
        'published': False,
    }
)
```

## Updating

### Unique Record

```py
post = await db.post.update(
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
total = await db.post.update_many(
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
post = await db.post.upsert(
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

### Updating Atomic Fields

If a field is an `int` or `float` type then it can be atomically updated, i.e. mathematical operations can be applied without knowledge of the previous value.

#### Integer Fields

```py
post = await db.post.update(
    where={
        'id': 'abc',
    },
    data={
        'views': 1,
        # or
        'views': {
            'set': 5,
            'increment': 1,
            'decrement': 2,
            'multiply': 5,
            'divide': 10,
        },
    },
)
```

#### Float Fields

```py
user = await db.user.update(
    where={
        'id': 'abc',
    },
    data={
        'points': 1.0,
        # or
        'points': {
            'set': 1.0,
            'increment': 1.5,
            'decrement': 0.5,
            'multiply': 2.5,
            'divide': 3.0,
        },
    },
)
```

### Updating List Fields

!!! warning
    Scalar list fields are only supported on PostgreSQL and MongoDB

```py
user = await db.user.update(
    where={
        'id': 'cksc9lp7w0014f08zdkz0mdnn',
    },
    data={
        'email': {
            'set': ['robert@craigie.dev', 'robert@example.com'],
            # or
            'push': ['robert@example.com'],
        },
    }
)
```

## Aggregrating

### Counting Records

```py
total = await db.post.count(
    where={
        'published': True,
    },
)
```
```py
total = await db.post.count(
    take=10,
    skip=1,
    where={
        'published': True,
    },
    cursor={
        'id': 'cksca3xm80035f08zjonuubik',
    },
)
```

### Grouping Records

!!! warning
    You can only order by one field at a time however this is [not possible
    to represent with python types](./limitations.md#grouping-records)

```py
results = await db.profile.group_by(['country'])
# [
#   {'country': 'Denmark'},
#   {'country': 'Scotland'},
# ]

results = await db.profile.group_by(['country'], count=True)
# [
#   {'country': 'Denmark', '_count': {'_all': 20}},
#   {'country': 'Scotland', '_count': {'_all': 1}},
# ]

results = await db.profile.group_by(
    by=['country', 'city'],
    count={
        '_all': True,
        'city': True,
    },
    sum={
        'views': True,
    },
    order={
        'country': 'desc',
    },
    having={
        'views': {
            '_avg': {
                'gt': 200,
            },
        },
    },
)
# [
#   {
#       'country': 'Scotland',
#       'city': 'Edinburgh',
#       '_sum': {'views': 250},
#       '_count': {'_all': 1, 'city': 1}
#   },
#   {
#       'country': 'Denmark',
#       'city': None,
#       '_sum': {'views': 6000},
#       '_count': {'_all': 12, 'city': 0}
#   },
#   {
#       'country': 'Denmark',
#       'city': 'Copenhagen',
#       '_sum': {'views': 8000},
#       '_count': {'_all': 8, 'city': 8}
#   },
# ]
```

## Batching Write Queries

```py
async with db.batch_() as batcher:
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
total = await db.execute_raw(
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
posts = await db.query_raw(
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

posts = await db.query_raw(
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
post = await db.query_first(
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

post = await db.query_first(
    '''
    SELECT *
    FROM Post
    WHERE Post.views > 50
    LIMIT 1
    ''',
    model=Post
)
```
