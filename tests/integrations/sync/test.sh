#!/bin/bash

set -eux

CURRENT_DIRECTORY=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
INTEGRATIONS_DIR=$(cd "${CURRENT_DIRECTORY}/.." && pwd)

source "${INTEGRATIONS_DIR}/common.sh"
setup_env

# required due to https://github.com/RobertCraigie/prisma-client-py/issues/35
HTTP=$(python -c 'import pathlib, prisma; print(pathlib.Path(prisma.__file__).parent / "http.py")')
cp ../../../prisma/http.py.original $HTTP 2>/dev/null || :

prisma db push --accept-data-loss --force-reset

coverage run -m pytest --confcutdir=. tests

pyright tests
