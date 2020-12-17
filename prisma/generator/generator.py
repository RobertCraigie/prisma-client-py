import logging
import argparse
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape


log = logging.getLogger(__name__)
BASE_PACKAGE_DIR = Path(__file__).parent.parent

__all__ = (
    'run',
)


def run(args):
    parser = argparse.ArgumentParser(description='Generate the prisma client code.')
    parser.add_argument('-o', '--output', type=str, help='directory to write the generated code to')

    parsed = parser.parse_args(args)
    rootdir = Path(parsed.output) if parsed.output else BASE_PACKAGE_DIR

    env = Environment(
        loader=PackageLoader('prisma.generator', 'templates'),
    )

    for name in env.list_templates():
        if not name.endswith('.py.jinja'):
            continue

        template = env.get_template(name)
        output = template.render()

        file = rootdir.joinpath(name.rstrip('.jinja'))
        file.write_text(output)
        log.debug('Wrote generated code to %s', file.absolute())
