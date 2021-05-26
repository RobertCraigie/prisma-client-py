import os
import sys
from pathlib import Path

sys.path.insert(0, '.')

from prisma.generator.generator import (  # pylint: disable=wrong-import-position
    BASE_PACKAGE_DIR,
    cleanup_templates,
)


def main() -> None:
    """Remove auto-generated python files"""
    cleanup_templates(rootdir=BASE_PACKAGE_DIR)
    cleanup_templates(rootdir=Path(os.environ.get('PRISMA_PY_OUTPUT')))


if __name__ == '__main__':
    main()
