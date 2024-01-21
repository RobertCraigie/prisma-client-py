from prisma.models import Post, User

Post.create_partial('PostWithAuthor', include=['id', 'title', 'author'])

User.create_partial('UserOnlyName', include=['name'])
Post.create_partial(
    'PostWithCustomAuthor',
    include=['id', 'title', 'author'],
    relations={
        'author': 'UserOnlyName',
    },
)

User.create_partial('UserWithPosts', include=['name', 'posts'])
Post.create_partial(
    'PostWithNestedRelations',
    include=['id', 'title', 'author'],
    relations={
        'author': 'UserWithPosts',
    },
)
