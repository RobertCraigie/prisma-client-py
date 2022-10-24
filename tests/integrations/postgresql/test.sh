#!/bin/bash

set -eux

CURRENT_DIRECTORY=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
INTEGRATIONS_DIR=$(cd "${CURRENT_DIRECTORY}/.." && pwd)

source "${INTEGRATIONS_DIR}/common.sh"
setup_env

prisma db push --accept-data-loss --force-reset

coverage run -m pytest --confcutdir=. tests

pyright
