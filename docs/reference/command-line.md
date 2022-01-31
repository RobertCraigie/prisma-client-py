# Command Line

<!-- TODO: this page should be more expansive -->

Prisma Client Python comes bundled with the [Prisma CLI](https://www.prisma.io/docs/reference/api-reference/command-reference), all commands and arguments are the same. You can invoke the CLI using the installed console script:

```
$ prisma db push
```

or by directly invoking the Prisma Client Python module:

```
$ python -m prisma db push
```

or if that fails for any reason, you can also use the standard Node Prisma CLI if you have `npx` installed:

```
$ npx prisma generate
```

!!! note
    If you use the Node CLI then the custom python commands are not available.
    However, you can still do everything else you would normally do with the Prisma CLI,
    including generating the Python Client!

## Commands

Prisma Client Python adds commands on top of the commands that [prisma provides](https://www.prisma.io/docs/reference/api-reference/command-reference).

All python commands must be prefixed by `py`

### Generate

Adds support for modifying Prisma Client Python schema [options](config.md) without having to make any changes to your prisma schema file.

```
Usage: prisma py generate [OPTIONS]

Options:
  --schema FILE               The location of the Prisma schema file.
  --watch                     Watch the Prisma schema and rerun after a change
  --interface [sync|asyncio]  Method that the client will use to interface
                              with Prisma
  --partials PATH             Partial type generator location
  -t, --type-depth INTEGER    Depth to generate pseudo-recursive types to; -1
                              signifies fully recursive types
  --help                      Show this message and exit.
```

### Version

Displays Prisma Client Python version information.

```
Usage: prisma py version [OPTIONS]

Options:
  --json  Output version information in JSON format.
  --help  Show this message and exit.
```

### Fetch

Ensure all binaries are downloaded and available.

```
Usage: prisma py fetch [OPTIONS]

Options:
  --force  Download all binaries regardless of if they are already downloaded
           or not.
  --help   Show this message and exit.
```
