from prisma.models import User

User.create_partial('UserWithoutRelations', exclude_relational_fields=True)
