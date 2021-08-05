#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

pip install -U pyright==0.0.5
pip install -U --find-links=../../../.tests_cache/dist prisma.io[requests]

TYPES=$(python -c 'import pathlib, prisma; print(pathlib.Path(prisma.__file__).parent / "types.py")')

pyright $TYPES
