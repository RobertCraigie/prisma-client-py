#!/bin/bash

set -eux

python3 -m venv .venv

set +x
source .venv/bin/activate
set -x

pip install -U 'pyright>=0.0.10' 'pytest'
pip install -U --force-reinstall ../../../.tests_cache/dist/*.whl

rm -f generated.md 2.md

prisma generate --schema=1.prisma
prisma generate --schema=2.prisma

pytest --confcutdir . test.py

pyright generator.py
