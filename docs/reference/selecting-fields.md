# Selecting Fields

Prisma Client Python supports selecting a subset of fields for improved performance & security when applicable, e.g. if there is a `hashed_password` field on your model.

Currently you must define your selections ahead of time and cannot dynamically select fields. This is because it is impossible to statically type queries using a dynamic syntax. See [this issue](https://github.com/RobertCraigie/prisma-client-py/issues/19) for discussion around potential solutions.

## Usage

There are two ways you can define a model type that can be used to select a certain subset of fields.

!!! tip

    While the pros and cons of both methods are outlined here, it should
    be fairly straightforward to move between the two as the way you write queries
    won't change.

The first is with [partial types](#with-partial-types) which should be used when:

- You plan on writing more than a couple queries with that particular model
- You know you're going to iterate heavily on your data model as partial types seamlessly evolve alongside your models

The second method is [defining the models yourself](#with-custom-models) which make it easier to write one-of queries or queries that are localised to small part of your application / data model.

??? note "Expand to show the example Prisma schema"

    ```prisma
    --8<-- "docs/src_examples/select-fields.schema.prisma"
    ```

### With Partial Types

!!! note

    If you're not familiar with [partial types](../getting_started/partial-types.md) then please read through the [docs](#../getting_started/partial-types.md) first.

Any partial type you define can also be used to run queries, for example:

```py
# partial type generator (e.g. `prisma/partial_types.py`)
from prisma.models import User

User.create_partial('UserWithName', include={'name'})
```

After updating your partial type generator and running `prisma generate` you can now import the type like so:

```py
from prisma.partials import UserWithName
```

See the [writing queries](#writing-queries) section for usage examples.

### With Custom Models

To define your own custom models you must import base model from `prisma.bases`. All base classes are defined using the `Base${model_name}` format.

For example, a schema with a `Comment` model will have a base class defined as `BaseComment`.

You can then define your own models in the exact same way you would using [pydantic](https://docs.pydantic.dev/).

For example, you could define a `User` model that only selected the `name` field like so:

```py
from prisma.bases import BaseUser

class UserWithName(BaseUser):
  name: str
```

See the [writing queries](#writing-queries) section for usage examples.

### Writing Queries

You can write select queries using the exact same syntax you would if you were writing queries using a [model](./model-actions.md) imported from `prisma.models`.

```py
user = await UserWithName.prisma().find_first(
  where={
    'country': 'Scotland',
  },
)
print(user.name)
```

If you ever try to access a field that doesn't exist on your custom model then type checkers will report an error and an error will be raised at runtime.

```py
print(user.id)  # error `id` does not exist on the `UserWithName` type
```

As you can see you can still query against fields that aren't defined on the model itself but Prisma Client Python will only select the fields that are present.

See the [Model Actions](./model-actions.md) documentation for more details on writing queries.

## Interaction With Relational Fields

!!! warning

    This feature is experimental and subject to change. See [this issue](https://github.com/RobertCraigie/prisma-client-py/issues/695) for discussion.

If in some cases you're writing a lot of queries that need to fetch the same relations over and over again it can be cumbersome and error-prone to have to explicitly specify them in `include`.

You can tell Prisma Client Python to always fetch one-to-many relations by defining the type as non-optional, for example:

```py
from typing import List
from prisma.models import Character
from prisma.bases import BaseUser

class UserWithCharacters(BaseUser):
  id: str
  name: str
  characters: List[Character]

user = await UserWithCharacters.prisma().find_unique(
  where={
    'id': '<user id>',
  },
)
print(user.name)
print(user.characters[0].strength)
```

With this `UserWithCharacters` definition, Prisma Client Python will always fetch the `characters` relation whenever you run a query using the `UserWithCharacters` model.

!!! warning

    Do not use this pattern everywhere in your codebase. Relational lookups can be expensive and result in a significant performance reduction if used unnecessarily.

!!! note

    It is not currently possible to use this pattern with one-to-one relational fields, please upvote or comment on [this issue](https://github.com/RobertCraigie/prisma-client-py/issues/695) if you wand this to be supported.
