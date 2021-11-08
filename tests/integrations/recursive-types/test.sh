#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

pip install -U 'pyright>=0.0.7'
pip install -U --force-reinstall ../../../.tests_cache/dist/*.whl

PRISMA=$(python -c 'import pathlib, prisma; print(pathlib.Path(prisma.__file__).parent)')

pyright $PRISMA
