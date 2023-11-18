# Interactive Transactions

!!! warning

    Transactions are not fully tested against CockroachDB.

Prisma Client Python supports interactive transactions, this is a generic solution allowing you to run multiple operations as a single, atomic operation - if any operation fails, or any other error is raised during the transaction, Prisma will roll back the entire transaction.

This differs from [batch queries](./batching.md) as you can perform operations that are dependent on the results of previous operations.

## Usage

Transactions can be created using the `Prisma.tx()` method which returns a context manager that when entered returns a separate instance of
`Prisma` that wraps all queries in a transaction.

=== "async"

    ```python
    from prisma import Prisma

    prisma = Prisma()
    await prisma.connect()

    async with prisma.tx() as transaction:
        user = await transaction.user.update(
            where={'id': from_user_id},
            data={'balance': {'decrement': 50}}
        )
        if user.balance < 0:
            raise ValueError(f'{user.name} does not have enough balance')

        await transaction.user.update(
            where={'id': to_user_id},
            data={'balance': {'increment': 50}}
        )
    ```

=== "sync"

    ```python
    from prisma import Prisma

    prisma = Prisma()
    prisma.connect()

    with prisma.tx() as transaction:
        user = transaction.user.update(
            where={'id': from_user_id},
            data={'balance': {'decrement': 50}}
        )
        if user.balance < 0:
            raise ValueError(f'{user.name} does not have enough balance')

        transaction.user.update(
            where={'id': to_user_id},
            data={'balance': {'increment': 50}}
        )
    ```

In this example, if the `ValueError` is raised then the entire transaction is rolled-back. This means that the first `update` call is reversed.

In the case that this example runs successfully, then both database writes are committed when the context manager exits, meaning that queries running elsewhere in your application will then access the updated data.

## Usage with Model Queries

!!! warning

    Transactions support alongside [model based queries](./model-actions.md) is not stable.

    Do **not** rely on `Model.prisma()` always using the default `Prisma` instance.
    This may be changed in the future.


=== "async"

    ```python
    from prisma import Prisma
    from prisma.models import User

    prisma = Prisma(auto_register=True)
    await prisma.connect()

    async with prisma.tx() as transaction:
        user = await User.prisma(transaction).update(
            where={'id': from_user_id},
            data={'balance': {'decrement': 50}}
        )
        if user.balance < 0:
            raise ValueError(f'{user.name} does not have enough balance')

        user = await User.prisma(transaction).update(
            where={'id': to_user_id},
            data={'balance': {'increment': 50}}
        )
    ```

=== "sync"

    ```python
    prisma = Prisma()
    prisma.connect()

    with prisma.tx() as transaction:
        user = User.prisma(transaction).update(
            where={'id': from_user_id},
            data={'balance': {'decrement': 50}}
        )
        if user.balance < 0:
            raise ValueError(f'{user.name} does not have enough balance')

        user = User.prisma(transaction).update(
            where={'id': to_user_id},
            data={'balance': {'increment': 50}}
        )
    ```

## Timeouts

You can pass the following options to configure how timeouts are applied to your transaction:

`max_wait` - The maximum amount of time Prisma will wait to acquire a transaction from the database. This defaults to `2 seconds`.

`timeout` - The maximum amount of time the transaction can run before being cancelled and rolled back. This defaults to `5 seconds`.


```py
from datetime import timedelta

prisma.tx(
    max_wait=timedelta(seconds=2),
    timeout=timedelta(seconds=10),
)
```
