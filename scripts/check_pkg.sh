#!/bin/bash

# sanity checks to ensure that auto-generated files are not included in the distribution

set -eu

output=$(git status src/prisma);

if [[ $output != *"working tree clean"* ]]; then
    echo "========== git status ==========";
    printf "$output\n";
    echo "================================";
    echo "It appears that there are modified files within src/prisma";
    echo "Please commit or stash the files before packaging.";
    exit 1;
else
    echo "git working tree is clean";
fi

echo "Ensuring package can be imported";

rm -rf .tests_cache/pkg-venv
python3 -m venv .tests_cache/pkg-venv
source .tests_cache/pkg-venv/bin/activate

set +e
output=$(pip install -U dist/*.whl 2>&1);
if [[ ! $? -eq 0 ]]; then
    printf "$output\n";
    echo "Error ocurred installing the client, see the above output.";
    exit 1;
fi
set -e

python -c 'import prisma';
python -m prisma --help > /dev/null

set +e
output=$(python -c 'import prisma.client' 2>&1);
if [[ $? -eq 0 ]]; then
    if [[ ! -z $output ]]; then
        echo "========= output ===========";
        printf "$output\n";
        echo "============================";
    fi

    echo "The prisma.client module was successfully imported";
    echo "This module should not be included in the package distribution.";
    echo "Please run make clean before packaging";
    exit 1;
fi
set -e

echo "Package is clean";
