import click


@click.command()
def cli() -> None:
    """Example command"""
    click.echo('Hello from example command!')
