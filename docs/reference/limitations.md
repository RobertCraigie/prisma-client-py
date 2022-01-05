# Limitations

## Type Limitations

!!! note
    It is highly recommended to use [pyright](https://github.com/microsoft/pyright) as your type
    checker of choice for Prisma Client Python applications.

Due to mypy limtations, some types are not as explicit as they should be and as such cannot
be considered fully type safe, however all of the limitations imposed by mypy can be removed
by switching to [pyright](https://github.com/microsoft/pyright) and [configuring prisma](config.md#recursive)
to use recursive types.

### Removing Limitations

You can catch all errors while type checking by using [pyright](https://github.com/microsoft/pyright)
and [configuring](config.md#recursive) prisma to use recursive types.

### Querying Using Model-based Access

Prisma Client Python supports querying directly from model classes, however, internally typing this feature to support subclassing with generics
causes mypy to be *incredibly* slow, it takes upwards of 35 minutes to type check the Prisma Client Python codebase on CI and upwards of 2 hours locally.

This kind of performance is not acceptable and as such, this typing has been disabled by default (switching to use recursive types will re-enable subclassing).

The downside of this is that static type checkers will not correctly recognise subclassed actions, for example:

```py
from prisma.models import User

class MyUser(User):
    pass

# static type checkers will think that `user` is an instance of `User`
# when it is actually an instance of `MyUser` at runtime
user = MyUser.prisma().create(
    data={
        'name': 'Robert',
    },
)
```

To combat this surprising behaviour, subclassing a prisma model will raise a warning at runtime.

```py
from prisma.models import User

class MyUser(User):  # warning: UnsupportedSubclassWarning
    pass
```

Warnings are raised using Pythons standard library [warnings](https://docs.python.org/3/library/warnings.html) module and can be disabled using [filters](https://docs.python.org/3/library/warnings.html#temporarily-suppressing-warnings) or by passing `warn_subclass=False` in the class definition, for example:

```py
from prisma.models import User

class MyUser(User, warn_subclass=False):
    pass
```

### Filtering by Relational Fields

Prisma supports searching for records based off of relational record values.
However, type checking this feature with mypy casued mypy to hang and eventually crash.

As such these types have been broadened, this means that mypy will not catch errors when
filtering by a relational field, for example, the following will not raise any mypy errors,
however an error will be raised at runtime.

```py
from prisma import Client

async def main(client: Client) -> None:
    user = await client.user.find_first(
        where={
            'profile': {
                'is': {
                    'an_invalid_value': 'foo',
                },
            },
        }
    )
```
