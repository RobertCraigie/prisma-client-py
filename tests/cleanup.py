import os
import sys
from pathlib import Path


# as we rely on prisma to cleanup the templates for us
# we have to make sure that prisma is importable and
# if any template rendered incorrect syntax or any other
# kind of error that wasn't automatically cleaned up,
# prisma will raise an error when imported,
# removing prisma/client.py fixes this as it is
# the only default entrypoint to generated code
file = Path(__file__).parent.parent / 'prisma/client.py'
if file.exists():
    file.unlink()

sys.path.insert(0, '.')

from prisma.generator.generator import (  # pylint: disable=wrong-import-position
    BASE_PACKAGE_DIR,
    cleanup_templates,
)


def main() -> None:
    """Remove auto-generated python files"""
    cleanup_templates(rootdir=BASE_PACKAGE_DIR)

    output = os.environ.get('PRISMA_PY_OUTPUT')
    if output is not None:
        cleanup_templates(rootdir=Path(output))


if __name__ == '__main__':
    main()
