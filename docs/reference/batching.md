# Batching Write Queries

In some cases you may want to insert a lot of rows at once or create two non-related models at the same time but only create the records if they all are created sucessfully. Prisma Client Python supports this by batching write queries.

Batching queries offers the exact same API as the standard Client with the exception of any finding queries such as `find_first` which are not supported.

Queries are not executed until `commit()` is called or the context manager exits.

## Examples

```py
async with db.batch_() as batcher:
    batcher.user.create({'name': 'Robert'})
    batcher.user.create({'name': 'Tegan'})
```

```py
batcher = db.batch_()
batcher.user.create({'name': 'Robert'})
batcher.user.create({'name': 'Tegan'})
await batcher.commit()
```
