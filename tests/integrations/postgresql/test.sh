#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

pip install -U -r requirements.txt
pip install -U --force-reinstall ../../../.tests_cache/dist/*.whl

prisma db push --accept-data-loss --force-reset

coverage run -m pytest --confcutdir=. tests

pyright
