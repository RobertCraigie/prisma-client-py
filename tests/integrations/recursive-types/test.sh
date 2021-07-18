#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

pip install -U -r requirements.txt

TYPES=$(python -c 'import pathlib, prisma; print(pathlib.Path(prisma.__file__).parent / "types.py")')

pyright $TYPES
