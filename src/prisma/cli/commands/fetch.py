import platform

import click

from ..utils import error


@click.command('fetch', short_help='Download all required binaries.')
@click.option(
    '--force',
    is_flag=True,
    help='Download all binaries regardless of if they are already downloaded or not.',
)
def cli(force: bool) -> None:
    """Ensures all required binaries are available."""
    from ... import binaries

    if force:
        if platform.system().lower() == 'windows':  # pragma: no cover
            error('The --force flag is not supported on Windows')

        binaries.remove_all()

    directory = binaries.ensure_cached()
    click.echo(f'Downloaded binaries to {click.style(str(directory), fg="green")}')
