#!/usr/bin/env bash

# This is a utility function that should be called from all the integration
# test.sh script entrypoints
function setup_env() {
    set -eux

    CURRENT_DIRECTORY=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
    PROJECT_ROOT=$(cd "${CURRENT_DIRECTORY}/../.." && pwd)

    echo "Setting up python virtuan environment in ${PWD}"

    python3 -m venv "${PWD}/.venv"

    set +x
    source "${PWD}/.venv/bin/activate"
    set -x

    # TODO: pytest-asyncio should not be required
    pip install -U -r "${PROJECT_ROOT}/pipelines/requirements/test.txt"
    pip install -U --force-reinstall "${PROJECT_ROOT}"/.tests_cache/dist/*.whl
}
