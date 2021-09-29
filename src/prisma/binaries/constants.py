import os
import tempfile
from pathlib import Path

from . import platform


__all__ = (
    'PRISMA_URL',
    'PRISMA_VERSION',
    'ENGINE_URL',
    'ENGINE_VERSION',
    'GLOBAL_TEMP_DIR',
    'PRISMA_CLI_NAME',
)


# TODO: if this version changes but the engine version
#       doesn't change then the CLI is incorrectly cached
# hardcoded CLI version version
PRISMA_VERSION = '3.1.1'

# CLI binaries are stored here
PRISMA_URL = os.environ.get(
    'PRISMA_CLI_URL',
    'https://prisma-photongo.s3-eu-west-1.amazonaws.com/prisma-cli-{version}-{platform}.gz',
)

# engine binaries are stored here
ENGINE_URL = os.environ.get(
    'PRISMA_ENGINE_URL', 'https://binaries.prisma.sh/all_commits/{0}/{1}/{2}.gz'
)

# versions can be found under https://github.com/prisma/prisma-engine/commits/master
ENGINE_VERSION = os.environ.get(
    'PRISMA_ENGINE_VERSION', 'c22652b7e418506fab23052d569b85d3aec4883f'
)

# where the binaries live
GLOBAL_TEMP_DIR = (
    Path(tempfile.gettempdir()) / 'prisma' / 'binaries' / 'engines' / ENGINE_VERSION
)

# local file path for the prisma CLI
if platform.name() == 'windows':  # pyright: reportConstantRedefinition=false
    PRISMA_CLI_NAME = f'prisma-cli-{platform.name()}.exe'
else:
    PRISMA_CLI_NAME = f'prisma-cli-{platform.name()}'
