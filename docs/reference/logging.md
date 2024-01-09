# Logging

Prisma Client Python uses python's [logging library](https://docs.python.org/3/library/logging.html) for logging messages.

## Debugging the CLI

Debugging the CLI is as simple as setting the `PRISMA_PY_DEBUG` environment variable to 1.

```sh
PRISMA_PY_DEBUG=1 prisma generate
```

## Debugging the Client

In order to display any debug messages in your terminal, the logging library must first be configured.

```py
import logging
logging.basicConfig()
```

This will not yet output any debug messages, in order to do so you must either:

* Set the `PRISMA_PY_DEBUG` environment variable to 1.

  or

* Programmatically enable debug messages

  ```py
  import logging
  logging.getLogger('prisma').setLevel(logging.DEBUG)
  ```
