#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

pip install -U -r requirements.txt

prisma db push --accept-data-loss --force-reset

pytest --confcutdir=. tests
