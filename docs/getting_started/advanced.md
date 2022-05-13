!!! note
    Adapted from the Prisma Client Go [documentation](https://github.com/prisma/prisma-client-go/blob/master/docs/advanced.md)

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
  id         String   @default(cuid()) @id
  created_at DateTime @default(now())
  content    String
  post       Post @relation(fields: [post_id], references: [id])
  post_id    String
}
```

??? note "Full Prisma Schema"
    ```prisma
    --8<-- "docs/src_examples/advanced.schema.prisma"
    ```

Whenever you make changes to your model, migrate your database and re-generate your prisma code:

```sh
# apply migrations
prisma migrate dev --name "add comment model"
# generate
prisma generate
```

In order to create comments, we can either create a post, and then connect that post when creating a comment or create a post while creating the comment.

```py
post = await db.post.create({
    'title': 'My new post',
    'published': True,
})
print(f'post: {post.json(indent=2)}\n')

first = await db.comment.create({
    'content': 'First comment',
    'post': {
        'connect': {
            'id': post.id,
        },
    },
})
print(f'first comment: {first.json(indent=2)}\n')

second = await db.comment.create({
    'content': 'Second comment',
    'post': {
        'connect': {
            'id': post.id,
        },
    },
})
print(f'second comment: {second.json(indent=2)}\n')
```

??? note "Alternative method"
    ```py
    first = await db.comment.create(
        data={
            'content': 'First comment',
            'post': {
                'create': {
                    'title': 'My new post',
                    'published': True,
                },
            },
        },
        include={'post': True}
    )
    second = await db.comment.create({
        'content': 'Second comment',
        'post': {
            'connect': {
                'id': first.post.id
            }
        }
    })
    ```

Now that a post and comments have been created, you can query for them as follows:

```py
# find all comments on a post
comments = await db.comments.find_many({
    'where': {
        'post_id': post.id
    }
})
print(f'comments of post with id {post.id}: {json.dumps(comments, indent=2)}')

# find at most 3 comments on a post
filtered = await db.comments.find_many({
    'where': {
        'post_id': post.id
    },
    'take': 3,
})
print(f'filtered comments of post with id {post.id}: {json.dumps(comments, indent=2)}')
```

Prisma also allows you to fetch multiple things at once. Instead of doing complicated joins, you can fetch a post and a
few of their comments in just a few lines and with full type-safety:

```py
# fetch a post and 3 of it's comments
post = await db.post.find_unique(
    where={
        'id': post.id,
    },
    include={
        'comments': {
            'take': 3,
        },
    },
)
```


<!-- TODO: add reference to the API reference documentation once added -->
