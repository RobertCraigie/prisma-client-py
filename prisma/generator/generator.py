import logging
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape


log = logging.getLogger(__name__)
BASE_PACKAGE_DIR = Path(__file__).parent.parent

__all__ = (
    'run',
)


def run():
    env = Environment(
        loader=PackageLoader('prisma.generator', 'templates'),
    )

    for name in env.list_templates():
        if not name.endswith('.py.jinja'):
            continue

        template = env.get_template(name)
        output = template.render()

        file = BASE_PACKAGE_DIR.joinpath(name.rstrip('.jinja'))
        file.write_text(output)
        log.debug('Wrote generated code to %s', file.absolute())
