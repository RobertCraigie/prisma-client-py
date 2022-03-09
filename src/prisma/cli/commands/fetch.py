import click


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
        binaries.remove_all()

    directory = binaries.ensure_cached()
    click.echo(
        f'Downloaded binaries to {click.style(str(directory), fg="green")}'
    )
