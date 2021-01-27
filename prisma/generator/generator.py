import logging
from pathlib import Path
from typing import Dict, Any
from distutils.dir_util import copy_tree

from jinja2 import Environment, PackageLoader

from .models import Data
from .utils import is_same_path


__all__ = ('run', 'BASE_PACKAGE_DIR')

log = logging.getLogger(__name__)
BASE_PACKAGE_DIR = Path(__file__).parent.parent


def run(params: Dict[str, Any]) -> None:
    params = vars(Data.parse_obj(params))
    rootdir = Path(params['generator'].output)
    if not rootdir.exists():
        rootdir.mkdir(parents=True, exist_ok=True)

    if not is_same_path(BASE_PACKAGE_DIR, rootdir):
        copy_tree(str(BASE_PACKAGE_DIR), str(rootdir))

    env = Environment(
        loader=PackageLoader('prisma.generator', 'templates'),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    for name in env.list_templates():
        if not name.endswith('.py.jinja') or name.startswith('_'):
            continue

        template = env.get_template(name)
        output = template.render(**params)

        file = rootdir.joinpath(name.rstrip('.jinja'))
        if not file.exists():
            file.parent.mkdir(parents=True, exist_ok=True)

        file.write_text(output)
        log.debug('Wrote generated code to %s', file.absolute())

    log.debug('Finished generating the prisma python client')
