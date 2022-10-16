# How To Contribute

First off, thank you for considering contributing to ``prisma-client-py``! It's people like _you_ who make it such a great tool for everyone.

This document intends to make contribution more accessible by codifying tribal knowledge and expectations. Don't be afraid to open half-finished PRs, and ask questions if something is unclear!

## General Prerequisites

You must have Python >= 3.7 installed on your system.

### Environment Variables

Running certain integration tests requires environment variables to be present, it is up to you to set these however you want to.

* **postgresql**: Set `PRISMA_PY_POSTGRES_URL` to any valid PostgreSQL connection string.

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

    Mypy checks can be ran with `tox -e mypy`

```sh
make format
tox -e setup,lint,py39,report
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

We use [tox](https://tox.readthedocs.io/) to run tests written with [pytest](https://docs.pytest.org/)

### Where Whould I Write The Test?

We have a few places where you can write tests:

* **Command Line**: `tests/test_cli/`
* **Client API**: `tests/test_*.py`
* **Client Generation**: `tests/test_generation`
* **Integration Tests**: `tests/integrations`
* **Type Tests**: `typesafety`

### Integration Tests

!!! note
    Running database integration tests requires certain environment variables to be present

Integration tests can be found in the `tests/integrations` directory. The entry point for each integration test is a `test.sh` script located at the top-level of the directory, e.g. `tests/integrations/postgresql/test.sh`.

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
tox -e py39 -- tests/integrations/
```

Or a specific test:

```sh
tox -e py39 -- --confcutdir . tests/integrations/postgresql
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


The tests can then be ran with tox, e.g.

```sh
tox -e py39
```

You can pass arguments directly to pytest like so:

```sh
tox -e py39 -- -x --ignore=tests/integrations
```

For writing good test docstrings see [this article](https://jml.io/pages/test-docstrings.html).

For a more specififc test case look through the tests and find one that is similar to what you need, don't be afraid to copy and paste test code.

### Snapshot Tests

We use [syrupy](https://github.com/tophat/syrupy) to manage our test snapshots. You can update the generated snapshots by running tests with `--snapshot-update`, for example:

```
tox -e py39 -- --snapshot-update tests/test_generation/exhaustive
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
tox -e typesafety-pyright
```

See the [pytest-pyright documentation](https://pytest-pyright.readthedocs.io/en/latest/#checking-for-errors) for more information.

#### Add Mypy Test

Mypy tests can be found in the `typesafety` directory.

To add a new test, simply create a `test_*.yml` file in the `typesafety` directory and run:

```sh
tox -e typesafety-mypy
```

See the [pytest-mypy-plugins documentation](https://github.com/TypedDjango/pytest-mypy-plugins) for more information.

## Docker Testing + Multi-Platform (CPU Architecture) Support

Since Github Actions (CI) does not allow for running code on multiple CPU architectures (and uses the amd64 aka x86_64 instruction set), we use a docker build process that uses its QEMU support to emulate multiple CPU platforms. The `make docker` command can be used to perform such a build locally. In CI this is enforced via the `docker` job in the test workflow.
