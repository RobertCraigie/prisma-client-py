#!/bin/bash

set -eux

CURRENT_DIRECTORY=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
INTEGRATIONS_DIR=$(cd "${CURRENT_DIRECTORY}/.." && pwd)

source "${INTEGRATIONS_DIR}/common.sh"
setup_env

prisma generate

# TODO: check the whole package
TYPES=$(python -c 'import pathlib, prisma; print(pathlib.Path(prisma.__file__).parent / "types.py")')
pyright $TYPES
