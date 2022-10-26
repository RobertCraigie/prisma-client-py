#!/bin/bash

set -eux

pip install -U --force-reinstall ../../../.tests_cache/dist/*.whl

# required due to https://github.com/RobertCraigie/prisma-client-py/issues/35
HTTP=$(python -c 'import pathlib, prisma; print(pathlib.Path(prisma.__file__).parent / "http.py")')
cp ../../../prisma/http.py.original $HTTP 2>/dev/null || :

prisma db push --accept-data-loss --force-reset

coverage run -m pytest --confcutdir=. tests

pyright tests
