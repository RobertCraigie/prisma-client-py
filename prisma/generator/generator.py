import sys
import logging
from pathlib import Path
from jinja2 import Environment, PackageLoader

from .utils import camelcase_to_snakecase


__all__ = ('run', 'BASE_PACKAGE_DIR')

log = logging.getLogger(__name__)
BASE_PACKAGE_DIR = Path(__file__).parent.parent

# TODO: not sure if all types are correct
type_mapping = {
    'String': 'str',
    'DateTime': 'datetime.datetime',
    'Boolean': 'bool',
    'Int': 'int',
    'Float': 'float',
    'Json': 'dict',
}


def run(params):
    rootdir = Path(params['generator']['output'])
    params = update_params(params)

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


def update_params(params):
    for model in params['dmmf']['datamodel']['models']:
        for field in model['fields']:
            try:
                field['python_type'] = type_mapping[field['type']]
            except KeyError:
                # TODO: handle this better
                raise RuntimeError(
                    f'Could not parse {field["name"]} in the {model["name"]} model '
                    f'due to unknown type: {field["type"]}',
                    file=sys.stderr,
                ) from None

            field['python_case'] = camelcase_to_snakecase(field['name'])

    return params
