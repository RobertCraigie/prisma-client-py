# Partial Types

Prisma Client Python exposes an interface for creating partial models at generation time based off of schema-defined models.
This is useful in situations where only certain fields of a model are available or certain fields are optional / required.

Partial models are generated to `prisma.partials`.

See [config](config.md#partial-type-generator) for configuration details and the [reference](reference/partials.md) for API documentation.

## Example

Given the following model and partial type generator

```schema.prisma
model User {
  id      String   @default(cuid()) @id
  name    String
  posts   Post[]
  email   String?
  profile Profile?
}
```

`.prisma/partials.py`
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
```

### Example Usage

Just like normal prisma models, partial models can be used anywhere that accepts a [pydantic BaseModel](https://pydantic-docs.helpmanual.io/usage/models).

One situation where partial types are particularly useful is in FastAPI endpoints

```py
from prisma.client import Client
from prisma.partials import UserWithoutRelations
from fastapi import FastAPI, Depends
from .utils import get_db

app = FastAPI()

@app.get(
    '/users/{user_id}',
    response_model=UserWithoutRelations,
)
async def get_user(user_id: str, db: Client = Depends(get_db)) -> User:
    return await db.user.find_unique(where={'id': user_id})
```
