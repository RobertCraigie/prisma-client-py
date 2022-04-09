# Model Based Access

Instead of using the traditional client based access to methods you can also query directly from the python models themselves:

```py
from prisma.models import User

user = await User.prisma().create(
    data={
        'name': 'Robert',
    },
)
```

!!! note
    This is not the same as the [Active Record Pattern](https://guides.rubyonrails.org/active_record_basics.html).

    These models (just like the models created using client-based access) carry persistent data but do not implement any behaviour that operates on the data. For example, updating a record would look something like this:

    ```py
    user = await User.prisma().update(
        where={
            'id': user.id,
        },
        data={
            'name': 'Robert',
        },
    )
    ```

## Registering a Client Instance

In order to query using model based access you must first create and register a client instance, for example:

```py
from prisma import Prisma

db = Prisma(auto_register=True)
```

or like this:

```py
import prisma

prisma.register(prisma.Prisma())
```

You can only do this once in the same python process.

You can also pass a function that returns a client instance.

```py
from prisma import Prisma, register

def get_client() -> Prisma:
    return Prisma()

register(get_client)
```

## Usage

All query operations are the *exact* same as with [client-based access](./operations.md).

Converting client-based access operations to model-based access operations simply requires changing calls like: `db.user` to `User.prisma()`.

### Examples

#### Creating a record

```py
from prisma.models import User

user = await User.prisma().create(
    data={
        'name': 'Robert',
    },
)
```

#### Finding a unique record

```py
from prisma.models import User

user = await User.prisma().find_unique(
    where={
        'id': '2',
    },
    include={
        'posts': True,
    },
)
```

#### Finding multiple records

```py
from prisma.models import Post

posts = await Post.prisma().find_many(
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
}
```

#### Updating a unique record

```py
from prisma.models import Post

post = await Post.prisma().update(
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

#### Executing raw queries

!!! warning
    SQL queries are sent directly to the database so you must use the syntax for your specific database provider

```py
from prisma.models import user

users = await User.prisma().query_raw(
    'SELECT * FROM User WHERE name = "?"', 'Robert'
)
```

```py
from prisma.models import user

user = await User.prisma().query_first(
    'SELECT * FROM User WHERE name = "?" LIMIT 1', 'Robert'
)
```
