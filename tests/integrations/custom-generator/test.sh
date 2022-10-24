#!/bin/bash

set -eux

CURRENT_DIRECTORY=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
INTEGRATIONS_DIR=$(cd "${CURRENT_DIRECTORY}/.." && pwd)

source "${INTEGRATIONS_DIR}/common.sh"
setup_env

rm -f generated.md 2.md

prisma generate --schema=1.prisma
prisma generate --schema=2.prisma

pytest --confcutdir . test.py

pyright generator.py
