# How To Contribute

First off, thank you for considering contributing to ``prisma-client-py``! It's people like _you_ who make it such a great tool for everyone.

This document intends to make contribution more accessible by codifying tribal knowledge and expectations. Don't be afraid to open half-finished PRs, and ask questions if something is unclear!

## General Prerequisites

You must have Python >= 3.7 installed on your system.

### Environment Variables

To be able to run the database tests you will have to define an environment variable for every database provider you want to run tests for, the full list of required environment variables can be found in `databases/example.env`.

```
SQLITE_URL='file:dev.db'
POSTGRES_URL='postgresql://<...>'
```

You can set these environment variables however you'd like to.

## Local Development Environment

Clone the repository

```sh
git clone https://github.com/RobertCraigie/prisma-client-py.git
cd prisma-client-py
```

Setup a virtual environment however you prefer, in this example we're using [venv](https://docs.python.org/3/library/venv.html)

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Bootstrap the directory, this command does the following:

- installs prisma-client-py in editable mode with all requirements
- creates a local SQLite database for testing
- installs pre-commit

```sh
make bootstrap
```

## Workflows

### Code Changes

After any code changes are made you must run linters and add tests to ensure your changes are valid.

You can run the linters and tests with coverage with the following commands.

!!! note
    These commands will not run mypy checks as it takes a significant amount of time to complete.

    Mypy checks can be ran with `nox -s mypy`

```sh
make format
nox -s setup lint
nox -s test -p 3.9
nox -s report
```

### Debugging Client Generation

Set the environment variable `PRISMA_PY_DEBUG_GENERATOR` to `1`, this will write the prisma DMMF data to your local directory at `src/prisma/generator/debug-data.json`.

### Documentation

The documentation for this project uses [mkdocs](https://www.mkdocs.org/) with the [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) theme.

While editing the docs you can start a local server and get live feedback with the following command:

```sh
make docs-serve
```

## Testing

We use [nox](https://nox.thea.codes/) to run tests written with [pytest](https://docs.pytest.org/)

### Where Whould I Write The Test?

We have a few places where you can write tests:

* **Command Line**: `tests/test_cli/`
* **Datbase Interactions**: `databases/tests`
* **Client Generation**: `tests/test_generation`
* **Integration Tests**: `tests/integrations`
* **Type Tests**: `typesafety`

### Database Tests

Prisma Client Python uses a custom testing suite to run client API tests against multiple database providers. These tests can be found in the `databases/tests` directory.

To be able run these tests you will need to have certain environment variables defined, see [Environment Variables](#environment-variables) for details on setting this up.

You can run these tests with:

```
nox -s databases -- test
```

Or you can explicitly specify the databases to run tests against:

```
nox -s databases -- test --databases=postgresql
```

This will generate the client for each given database and do the following:

- Run pytest over all tests enabled for the given database provider
- Run Pyright over the generated client code and all enabled test files

These tests work by splitting up database specific features into their own directories / files and then depending on which database you are running the tests for, excluding certain files.

### Integration Tests

!!! note
    Running database integration tests requires certain environment variables to be present

Integration tests can be found in the `tests/integrations` directory. The entry point for each integration test is a `test.sh` script located at the top-level of the directory, e.g. `tests/integrations/custom-generator/test.sh`.

You can do whatever you need to within this file, however, every `test.sh` should start with:

```sh
#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x
```

To install the prisma package in your integration test you can add the following commands, replacing `<EXTRA>` with whatever extra you need to be installed.

```sh
pip install -U -r ../../../requirements/<EXTRA>.txt
pip install -U --force-reinstall ../../../.tests_cache/dist/*.whl
```

You can now add whatever integration specific commands you need.

You can run the integration tests only with the following command:

```sh
nox -s test -p 3.9 -- tests/integrations/
```

Or a specific test:

```sh
nox -s test -p 3.9 -- --confcutdir . tests/integrations/postgresql
```

!!! warning
    You may also need to update the root `pytest.ini` file to include your integration test in the `norecursedirs` option if you run pytest within the integration test

### Unit Tests

<!-- TODO: All files in the `tests` directory must maintain `100%` coverage. -->

Unit tests are ran with [pytest](https://docs.pytest.org/), every test case must include a docstring.

To add a test case find the appropriate test file in the `tests` directory (if no file matches feel free to create a new one) and you can test the client like so:

```py
import pytest
from prisma import Prisma

@pytest.mark.asyncio
async def test_example(client: Prisma) -> None:
    """Test docstring"""
    ...
```

If the test you are writing makes use of model-based access then you must mark the test like so:

```py
import pytest

@pytest.mark.prisma
@pytest.mark.asyncio
async def test_example() -> None:
    """Test docstring"""
    ...
```


The tests can then be ran with nox, e.g.

```sh
nox -s test -p 3.9
```

You can pass arguments directly to pytest like so:

```sh
nox -s test -p 3.9 -- -x --ignore=tests/integrations
```

For writing good test docstrings see [this article](https://jml.io/pages/test-docstrings.html).

For a more specififc test case look through the tests and find one that is similar to what you need, don't be afraid to copy and paste test code.

### Snapshot Tests

We use [syrupy](https://github.com/tophat/syrupy) to manage our test snapshots. You can update the generated snapshots by running tests with `--snapshot-update`, for example:

```
nox -s test -p 3.9 -- --snapshot-update tests/test_generation/exhaustive
```

### Type Tests

In order to ensure types have been implemented correctly we use [pytest-pyright](https://pytest-pyright.readthedocs.io/) and [pytest-mypy-plugins](https://github.com/TypedDjango/pytest-mypy-plugins).

You can run both pyright and mypy tests with

```sh
make typesafety
```

#### Add Pyright Test

To add a new test, simply create a `.py` file in the `typesafety/pyright` directory and run:

```sh
nox -s typesafety-pyright
```

See the [pytest-pyright documentation](https://pytest-pyright.readthedocs.io/en/latest/#checking-for-errors) for more information.

#### Add Mypy Test

Mypy tests can be found in the `typesafety` directory.

To add a new test, simply create a `test_*.yml` file in the `typesafety` directory and run:

```sh
nox -s typesafety-mypy
```

See the [pytest-mypy-plugins documentation](https://github.com/TypedDjango/pytest-mypy-plugins) for more information.

## Docker Testing + Multi-Platform (CPU Architecture) Support

Since Github Actions (CI) does not allow for running code on multiple CPU architectures (and uses the amd64 aka x86_64 instruction set), we use a docker build process that uses its QEMU support to emulate multiple CPU platforms. The `make docker` command can be used to perform such a build locally. In CI this is enforced via the `docker` job in the test workflow.

We also use a docker build arg for the `OS_DISTRO` so that we can try and test against several of the official upstream [Python docker image flavors](https://hub.docker.com/_/python).

**NOTE:** The docker setup should only be used internally for testing and not for re-distribution via a remote registry.
