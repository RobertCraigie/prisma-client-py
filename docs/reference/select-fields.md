# Selecting Fields

Prisma Client Python supports selecting a subset of fields for improved performance & security in some cases.

Currently you must define your selections ahead of time and cannot dynamically select fields. See Limitations (TODO) for why this is the case.

## Reference

> Please see the [Example Usage Guide](#example-usage-guide) for a more guided walkthrough of how to select fields.

TODO

## Example Usage Guide

The easiest way to get started with selecting fields is by using [Partial Types](partials.md) to define the fields you want to select so that Prisma Client Python can generate a partial representation of the given model so that you don't have to define it entirely yourself and so that it can easily evolve alongside your data models.

<!-- To get started, we'll first have to tell Prisma Client Python how -->

For this guide we'll define a `User` model.

```prisma
model User {
  id              String @id @default(cuid())
  name            String
  email           String
  hashed_password String
}
```

Now, in our imagined application, very few parts should

Now, let's imagine that in our application we very rarely have to access the `hashed_password` field and as this is field should be treated with caution TODO

<!-- TODO: reword -->

Now, as the majority of the usage of the `User` model in our application doesn't make use of the `hashed_password` field and it is a source of security concern, we don't want to accidentally expose this somewhere it shouldn't be.

Let's generate a partial type that doesn't have this field included.

Create a file at `prisma/partial_types.py` and include this snippet:

```python
from prisma.models import User

User.create_partial('UserSelect', exclude={'hashed_password'})
```

TODO: verify above works

Now run `prisma generate`,

```
$ prisma generate
TODO: output
```

We can now write queries using the `UserSelect` model like we would any other standard model and Prisma Client Python will exclude the `hashed_password` field at the database level.

```python
from prisma.partials import UserSelect


user = await UserSelect.prisma().create(
    {
        'name': 'Robert',
        'email': 'robert@craigie.dev',
        'hashed_password': '...'
    }
)
print(user.json(indent=2))
"""
{
    "name": "Robert",
    "email": "robert@craigie.dev"
}
"""
```

TODO: warning about nominal subtyping (in reference instead / both?)

TODO: showcase defining custom helpers directly on the model
