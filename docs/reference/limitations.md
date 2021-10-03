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
