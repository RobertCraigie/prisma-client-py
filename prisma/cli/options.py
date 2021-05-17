import click

from .utils import PathlibPath


schema = click.option(
    '--schema',
    type=PathlibPath(exists=True, dir_okay=False, resolve_path=True),
    help='The location of the Prisma schema file.',
    required=False,
)

watch = click.option(
    '--watch',
    is_flag=True,
    default=False,
    required=False,
    help='Watch the Prisma schema and rerun after a change',
)
