# Mypy

We provide a mypy plugin for extending type checking functionality and improving ease of use.

## Setup

Create or modify the [mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html) (default: `mypy.ini`) so that it looks like the following:

```
[mypy]
plugins = prisma.mypy
```

## Configuration

Options are passed to the mypy plugin through the [mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html) under the `[prisma-mypy]` key.

```
[prisma-mypy]
option = True
```

### Warn Parsing Errors

Prisma will raise a parsing error if it cannot resolve a value, for example, the following will raise an error as the value for the include argument currently cannot be resolved.

!!! note
    This does not mean there is a type error with the code, this error is simply a warning that the plugin could not apply certain functionality.

```py
from prisma.types import UserInclude

include = dict()  # type: UserInclude
include['posts'] = True
user = await db.user.find_unique(
    where={
      'id': 'user_id',
    },
    include=include,
)
```

This error can be disabled in two ways:

* Inline

```py
user = await db.user.find_unique(
    where={
        'id': 'user_id',
    },
    include=include  # type: ignore[prisma-parsing]
)
```

* Globally

This behaviour can be controlled with the boolean `warn_parsing_errors` config option.

Adding the following to the [mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html) will disable the error throughout your project.

```
[prisma-mypy]
warn_parsing_errors = False
```

## Features

### Removes Optional From Relational Fields

If a relational field is explicitly passed with `include`, the field on the returned model will no longer be typed as `Optional` (if applicable).

For example, without the plugin the following snippet would have raised an error that `user.posts` can be `None`, however as we are explicitly including the user's posts, the posts attribute will never be `None` in this context.

!!! note
    If no posts are found then `user.posts` will be an empty list

```py
user = await db.user.find_unique(
    where={
        'id': 'user_id',
    },
    include={
        'posts': True
    }
)
print(f'User {user.name} has {len(user.posts)} posts')
```

It should be noted that if a relation is optional in the schema, the relational field will still be typed as `Optional` even when explicitly included, for example, the following will raise an error that the `profile` can be `None`

```py
user = await db.user.find_unique(
    where={
        'id': 'user_id',
    },
    include={
        'profile': True,
    }
)
print(f'User {user.name}, bio: {user.profile.bio}')
```

It should be noted that a dynamic `include` value is not currently supported, for example, the following will raise an error. See [here](#warn-parsing-errors) for how to disable the error.

```py
from prisma.types import UserInclude

include = dict()  # type: UserInclude
include['posts'] = True
user = await db.user.find_unique(
    where={
        'id': 'user_id',
    },
    include=include,
)
```
