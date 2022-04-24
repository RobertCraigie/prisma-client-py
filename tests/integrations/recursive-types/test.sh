#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

pip install -U -r requirements.txt
pip install -U --force-reinstall ../../../.tests_cache/dist/*.whl

prisma generate

# TODO: check the whole package
TYPES=$(python -c 'import pathlib, prisma; print(pathlib.Path(prisma.__file__).parent / "types.py")')
pyright $TYPES
