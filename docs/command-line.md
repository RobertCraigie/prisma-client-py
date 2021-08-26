# Command Line

<!-- TODO: this page should be more expansive -->

## Commands

Prisma Client Python adds commands on top of the commands that [prisma provides](https://www.prisma.io/docs/reference/api-reference/command-reference).

All python commands must be prefixed by `py`

### Generate

Adds support for modifying Prisma Client Python schema [options](config.md) without having to make any changes to your prisma schema file.

```
Usage: prisma py generate [OPTIONS]

Options:
  --schema FILE              The location of the Prisma schema file.
  --watch                    Watch the Prisma schema and rerun after a change
  --http [aiohttp|requests]  HTTP client library the generated client will use
  --partials PATH            Partial type generator location
  --help                     Show this message and exit.
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
