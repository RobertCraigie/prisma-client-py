# Schema Extensions

Prisma Client Python supports extensions to the standard [Prisma Schema syntax](https://www.prisma.io/docs/orm/prisma-schema/overview) in the form of `/// @Python(...)` comments.

Note that the number of forward-slashes here is important, if you only use `//` then your comment won't be passed down to Prisma Client Python as it's interpreted as a comment relating to the schema itself.

The arguments that you can pass to `@Python()` depend on the context it's used in, currently only models are supported.

## Model Extensions

### `instance_name`

You can customise the name of the property that each model in your schema is generated to using the `instance_name` argument, e.g.

```prisma
/// @Python(instance_name: "org_member")
model OrgMember {
  // ...
}
```

Will result in:

```py
class Prisma:
    org_member: OrgMember

# ...
client = Prisma()
client.org_member.find_unique(...)
```
