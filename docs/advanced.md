## Advanced usage

> NOTE: Adapted from the Prisma Client Go [documentation](https://github.com/prisma/prisma-client-go/blob/master/docs/advanced.md)

In the [quickstart](quickstart.md), we have created a simple post model and ran a few queries. However, Prisma and the
Python client are designed to work with relations between models.

We already created a post model, such as for a blog. Let's assume we want to add comments to a post, and connect these
models in a way so we can rely on SQL's foreign keys and the Python client's ability to work with relations.

So let's introduce a new comment model with a 1 to many relationship with the Post model:

```prisma
model Post {
    ...
    comments Comment[]
}

model Comment {
    id        String   @default(cuid()) @id
    createdAt DateTime @default(now())
    content   String
    post   Post @relation(fields: [post_id], references: [id])
    post_id String
}
```

<details>
    <summary>Expand to show full schema.prisma</summary>

   ```prisma
    datasource db {
        // could be postgresql or mysql
        provider = "sqlite"
        url      = "file:dev.db"
    }

    generator db {
        provider = "python -m prisma"
    }

    model Post {
        id        String   @default(cuid()) @id
        createdAt DateTime @default(now())
        updatedAt DateTime @updatedAt
        title     String
        published Boolean
        desc      String?
        comments Comment[]
    }

    model Comment {
        id        String   @default(cuid()) @id
        createdAt DateTime @default(now())
        content   String
        post   Post @relation(fields: [post_id], references: [id])
        post_id String
    }
   ```

</details>

Whenever you make changes to your model, migrate your database and re-generate your prisma code:

```shell script
# apply migrations
python -m prisma migrate save --experimental --name "add comment model"
python -m prisma migrate up --experimental
# generate
python -m prisma generate
```

In order to create comments, we first need to create a post, and then connect that post when creating a comment.

```py
post = await client.post.create({'title': 'My new post', 'published': True})
print(f'post: {post.json(indent=2)}\n')

first = await client.comment.create({'content': 'First comment', 'post': {'connect': {'id': post.id}}})
print(f'first comment: {first.json(indent=2)}\n')

second = await client.comment.create({'content': 'Second comment', 'post': {'connect': {'id': post.id}}})
print(f'second comment: {second.json(indent=2)}\n')
```

Now that a post and comments have been created, you can query for them as follows:

```py
# find all comments on a post
comments = await client.comments.find_many({'where': {'post_id': post.id}})
print(f'comments of post with id {post.id}: {json.dumps(comments, indent=2)}')

# find at most 3 comments on a post
filtered = await client.comments.find_many({'where': {'post_id': post.id}, 'take': 3})
print(f'filtered comments of post with id {post.id}: {json.dumps(comments, indent=2)}')
```

Prisma also allows you to fetch multiple things at once. Instead of doing complicated joins, you can fetch a post and a
few of their comments in just a few lines and with full type-safety:

```py
# fetch a post and 3 of it's comments
post = await client.post.find_unique(where={'post_id': post.id}, include={'comments': {'take': 3}})
```

## API reference

To explore all query capabilities, check out the [API reference](reference).

