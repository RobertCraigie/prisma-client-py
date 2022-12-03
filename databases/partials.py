from prisma.models import Post

Post.create_partial('PostOnlyPublished', include={'id', 'published'})
