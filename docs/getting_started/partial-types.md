# Partial Types

Prisma Client Python exposes an interface for creating partial models at generation time based off of schema-defined models.
This is useful in situations where only certain fields of a model are available or certain fields are optional / required.

Partial models are generated to `prisma.partials`.

See [config](../reference/config.md#partial-type-generator) for configuration details and the [reference](../reference/partials.md) for API documentation.

## Example

Given the following model and partial type generator

```prisma
model User {
  id      String   @default(cuid()) @id
  name    String
  posts   Post[]
  email   String?
  profile Profile?
}
```

`prisma/partial_types.py`
```py
from prisma.models import User

# user with only email and name
User.create_partial('UserInLogin', include={'email', 'name'})

# user with a non-optional email field
User.create_partial('UserWithEmail', required={'email'})

# normal user model without an email
User.create_partial('UserWithoutEmail', exclude={'email'})

# user with a non-optional profile
User.create_partial('UserWithProfile', required={'profile'})

# user with an optional name
User.create_partial('UserWithOptionalName', optional={'name'})

# user without any relational fields (in this case without the profile and posts fields)
User.create_partial('UserWithoutRelations', exclude_relational_fields=True)
```
Would generate the following partial types
```py
class UserInLogin(BaseModel):
    name: str
    email: Optional[str]

class UserWithEmail(BaseModel):
    id: str
    name: str
    email: str
    posts: Optional[List[models.Post]]
    profile: Optional[models.Profile]

class UserWithoutEmail(BaseModel):
    id: str
    name: str
    posts: Optional[List[models.Post]]
    profile: Optional[models.Profile]

class UserWithProfile(BaseModel):
    id: str
    name: str
    email: Optional[str]
    posts: Optional[List[models.Post]]
    profile: models.Profile

class UserWithOptionalName(BaseModel):
    id: str
    name: Optional[str]
    email: Optional[str]
    posts: Optional[List[models.Post]]
    profile: Optional[models.Profile]

class UserWithoutRelations(BaseModel):
    id: str
    name: str
    email: Optional[str]
```

### Example Usage

Just like normal prisma models, partial models can be used anywhere that accepts a [pydantic BaseModel](https://docs.pydantic.dev/latest/usage/models/).

One situation where partial types are particularly useful is in FastAPI endpoints

```py
from typing import Optional
from prisma import Prisma
from prisma.partials import UserWithoutRelations
from fastapi import FastAPI, Depends
from .utils import get_db

app = FastAPI()

@app.get(
    '/users/{user_id}',
    response_model=UserWithoutRelations,
)
async def get_user(user_id: str, db: Prisma = Depends(get_db)) -> Optional[User]:
    return await db.user.find_unique(where={'id': user_id})
```

or for making raw queries type safe

```py
from prisma.partials import UserInLogin

user = await db.query_first(
    'SELECT name, email FROM User WHERE id = ?',
    'abc',
    model=UserInLogin,
)
if user is None:
    print('Did not find user')
else:
    print(f'Found user: name={user.name}, email={user.email}')
```
