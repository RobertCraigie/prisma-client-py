import logging
from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, PackageLoader
from .models import Data


__all__ = ('run', 'BASE_PACKAGE_DIR')

log = logging.getLogger(__name__)
BASE_PACKAGE_DIR = Path(__file__).parent.parent


def run(params: Dict[str, Any]) -> None:
    params = vars(Data.parse_obj(params))
    rootdir = Path(params['generator'].output)

    env = Environment(
        loader=PackageLoader('prisma.generator', 'templates'),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    header = env.get_template('_header.py.jinja').render(**params)

    for name in env.list_templates():
        if not name.endswith('.py.jinja') or name.startswith('_'):
            continue

        template = env.get_template(name)
        output = header + template.render(**params)

        file = rootdir.joinpath(name.rstrip('.jinja'))
        file.write_text(output)
        log.debug('Wrote generated code to %s', file.absolute())

    log.debug('Finished generating the prisma python client')
