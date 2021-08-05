#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

pip install -U -r requirements.txt
pip install -U --find-links=../../../.tests_cache/dist prisma.io[aiohttp]

prisma db push --accept-data-loss --force-reset

pytest --confcutdir=. tests

pyright
