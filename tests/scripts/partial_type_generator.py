from prisma.models import Post

# post with only id and published
Post.create_partial('PostOnlyPublished', include={'id', 'published'})
