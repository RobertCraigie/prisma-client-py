import sys
import pkgutil
from pathlib import Path


# as we rely on prisma to cleanup the templates for us
# we have to make sure that prisma is importable and
# if any template rendered incorrect syntax or any other
# kind of error that wasn't automatically cleaned up,
# prisma will raise an error when imported,
# removing prisma/client.py fixes this as it is
# the only default entrypoint to generated code
file = Path(pkgutil.get_loader('prisma').get_filename()).parent / 'client.py'
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


if __name__ == '__main__':
    main()
