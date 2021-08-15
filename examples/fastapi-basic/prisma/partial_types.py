from prisma.models import User, Post

User.create_partial('UserWithoutRelations', exclude={'posts'})
Post.create_partial('PostWithoutRelations', exclude={'author'})
