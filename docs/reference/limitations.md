# Limitations

There are two forms of limitations imposed on Prisma Client Python, the [first](#default-type-limitations) is due to missing features / performance issues with mypy and can be re-enabled by switching to use `pyright instead`. The [second](#python-limitations) is due to scenarios that cannot be accurately represented within Python's type system.

## Default Type Limitations

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

Prisma Client Python supports querying directly from model classes, however, internally typing this feature to support subclassing with generics causes mypy to be *incredibly* slow, it takes upwards of 35 minutes to type check the Prisma Client Python codebase on CI and upwards of 2 hours locally.

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
from prisma import Prisma

async def main(db: Prisma) -> None:
    user = await db.user.find_first(
        where={
            'profile': {
                'is': {
                    'an_invalid_value': 'foo',
                },
            },
        }
    )
```

### Complex Grouping Arguments

Mypy does not support Literal TypeVars which means the following invalid code will not produce an error when type checking:

```py
results = await Profile.prisma().group_by(
    by=['country'],
    order={
        # city has to be included in the `by` argument to be valid
        'city': True,
    }
)
```

This error can be revealed by switching to [pyright](https://github.com/microsoft/pyright) and [configuring prisma](config.md#recursive)
to use recursive types.

## Python Limitations

There are some limitations to type safety due to Python's inability to expressively work with input types. While it would be *possible* to work around this as Prisma Client Python code is auto-generated, we need to strike a balance between performance and correctness.

These limitations only effect **2** arguments in one query method in the **entire** client API.

### Grouping records

#### Explanation

Some filters can only be performed on fields that are being grouped (i.e. in the `by` argument), this is not possible to type in Python with any accuracy. It is possible to limit dictionary keys but it is not possible to match the dictionary keys to specific types like you can with a standard `TypedDict`.

For example, the `order` argument can correctly limit the available keys as all the values have the same type

```py
results = await Profile.prisma().group_by(
    by=['city'],
    order={
        'city': 'asc',
        # this will error as 'country' is not present in the `by` argument
        'country': 'desc',
    },
)
```

However this is not possible with the `having` argument as all the dictionary values have different types.

```py
# this error will NOT be caught by static type checkers!
# but it will raise an error at runtime
results = await Profile.prisma().group_by(
    by=['city'],
    having={
        'views': {
            'gt': 50,
        },
    },
)
```

#### Limitations

##### Order Argument

The `order` argument can only take one field at a time.

The following example will pass type checks but will raise an error at runtime.

```py
results = await Profile.prisma().group_by(
    by=['city', 'country'],
    order={
        'city': 'asc',
        'country': 'desc',
    },
)
```

##### Having Argument

The `having` argument only takes fields that are present in the `by` argument **or** aggregation filters.

For example:

```py
# this will pass type checks but will raise an error at runtime
# as 'views' is not present in the `by` argument
await Profile.prisma().group_by(
    by=['country'],
    count=True,
    having={
        'views': {
            'gt': 50,
        },
    },
)

# however this will pass both type checks and at runtime!
await Profile.prisma().group_by(
    by=['country'],
    count=True,
    having={
        'views': {
            '_avg': {
                'gt': 50,
            },
        },
    },
)
```
