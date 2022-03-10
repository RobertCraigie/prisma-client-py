# Troubleshooting

This page contains tips to resolve common Prisma Client Python errors. If you've encountered an error that isn't listed on this page then please share it and we'll add it!

## Cannot import client

In some situations it is possible that your Prisma Client Python installation becomes corrupted, this mainly occurs when upgrading from one version to another, if this is the case then we provide a helpful utility package independent of Prisma Client Python that will remove all the files that are auto-generated.

You can call it from the command line:

```
python -m prisma_cleanup
```

Or programmatically

```py
from prisma_cleanup import cleanup

cleanup()
```

### Custom client

If you are using a custom output directory for Prisma Client Python then you simply have to pass the import path to `prisma_cleanup`, for example:

```
python -m prisma_cleanup app.prisma
```

For a custom output defined like this

```prisma
generator py {
  provider = "prisma-client-py"
  output   = "app/prisma"
}
