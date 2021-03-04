# Partial Types

Prisma Client Python exposes an interface for creating partial models at generation time based off of schema-defined models, see [partial-types](../partial-types.md) for more information.

Each model defined in the schema can have partial types generated based off of it. The API looks like this:
```py
class Model:
  @staticmethod
  def create_partial(
      name: str,
      include: Optional[Iterable['{{ model }}Keys']] = None,
      exclude: Optional[Iterable['{{ model }}Keys']] = None,
      required: Optional[Iterable['{{ model }}Keys']] = None,
      optional: Optional[Iterable['{{ model }}Keys']] = None,
  ) -> None:
      ...
```
where `{{ model }}Keys` is [Literal](https://docs.python.org/3/library/typing.html#typing.Literal) type containing all the fields of the model.

For example:

```schema.prisma
...
model User {
  id      String   @default(cuid()) @id
  name    String
  posts   Post[]
  email   String?
}
...
```

```py
UserKeys = Literal['id', 'name', 'posts', 'email']
```

## Reference

* `name`

  The name given to the generated partial type, must be unique.

* `include`

  An iterable of field names that will be available in the generated model.
  Cannot be used at the same time as `exclude`.

* `exclude`

  An iterable of field names that will *not* be available in the generated model.
  Cannot be used at the same time as `include`.

* `required`

  An iterable of field names that will *not* be marked as optional in the generated model.

* `optional`

  An iterable of field names that will be marked as optional in the generated model.

## Examples

All examples use the following models

```schema.prisma
model User {
  id      String   @default(cuid()) @id
  name    String
  profile Profile
  email   String?
}

model Profile {
  id       Int    @id @default(autoincrement())
  user     User   @relation(fields:  [userId], references: [id])
  user_id  String
  bio      String
}
```

```py
class User:
  id: str
  name: str
  profile: Optional['Profile']
  profile_id: int
  email: Optional[str]

class Profile:
  id: int
  user: Optional['User']
  user_id: str
  bio: str
```


### Include

```py
from prisma.models import User
User.create_partial('UserOnlyName', include={'name'})
User.create_partial('UserOnlyNameAndEmail', include={'name', 'email'})
```

```py
class UserOnlyName:
  name: str

class UserOnlyNameAndEmail:
  name: str
  email: Optional[str]
```


### Exclude

```py
from prisma.models import User
User.create_partial('UserWithoutProfile', exclude=['profile', 'profile_id'])
```

```py
class UserWithoutProfile:
  id: str
  name: str
  email: Optional[str]
```

### Optional

```py
from prisma.models import User
User.create_partial('UserOptionalName', optional={'name'})
```

```py
class UserOptionalName:
  id: str
  name: Optional[str]
  profile: Optional['Profile']
  profile_id: int
  email: Optional[str]
```

### Required

```py
from prisma.models import User
User.create_partial('UserRequiredEmail', required={'email'})
```

```py
class UserRequiredEmail:
  id: str
  name: str
  profile: Optional['Profile']
  profile_id: int
  email: str
```

