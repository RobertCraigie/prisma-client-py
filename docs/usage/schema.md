# Schema

Every project that uses a tool from the Prisma toolkit starts with a [Prisma schema file](https://www.prisma.io/docs/concepts/components/prisma-schema). The Prisma schema allows developers to define their _application models_ in an intuitive data modeling language. It also contains the connection to a database and defines a _generator_.

TODO

```prisma
// database
datasource db {
  provider = "sqlite"
  url      = "file:database.db"
}

// generator
generator client {
  provider = "prisma-client-py"
}

// data models
model Post {
  id        Int     @id @default(autoincrement())
  title     String
  content   String?
  views     Int     @default(0)
  published Boolean @default(false)
  author    User?   @relation(fields: [author_id], references: [id])
  author_id Int?
}

model User {
  id    Int     @id @default(autoincrement())
  email String  @unique
  name  String?
  posts Post[]
}
```
