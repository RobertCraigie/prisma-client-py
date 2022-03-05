#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

# TODO: pytest-asyncio should not be required
pip install -U pytest==6.2.4 pytest-asyncio==0.17.0 pyright coverage==6.1.1
pip install -U --force-reinstall ../../../.tests_cache/dist/*.whl

# required due to https://github.com/RobertCraigie/prisma-client-py/issues/35
HTTP=$(python -c 'import pathlib, prisma; print(pathlib.Path(prisma.__file__).parent / "http.py")')
cp ../../../prisma/http.py.original $HTTP 2>/dev/null || :

prisma db push --accept-data-loss --force-reset

coverage run -m pytest --confcutdir=. tests

pyright tests
