from typing import Optional, cast

import click

from .. import options
from ..utils import generate_client, error
from ...utils import maybe_async_run, temp_env_update, module_exists


@click.group()
def cli() -> None:
    """Commands for developing Prisma Client Python"""


@cli.command()
@options.schema
@options.skip_generate
def playground(schema: Optional[str], skip_generate: bool) -> None:
    """Run the GraphQL playground"""
    if skip_generate and not module_exists('prisma.client'):
        error('Prisma Client Python has not been generated yet.')
    else:
        generate_client(schema=schema, reload=True)

    # TODO: this assumes we are generating to the same location that we are being invoked from
    from ... import Client
    from ...engine import QueryEngine

    client = Client()
    engine_class = client._engine_class  # pylint: disable=protected-access
    if engine_class.__name__ == 'QueryEngine':
        with temp_env_update({'__PRISMA_PY_PLAYGROUND': '1'}):
            maybe_async_run(client.connect)

        # TODO: this is the result of a badly designed class
        engine = cast(QueryEngine, client._engine)  # pylint: disable=protected-access
        assert engine.process is not None, 'Engine process unavailable for some reason'
        engine.process.wait()
    else:  # pragma: no cover
        error(f'Unsupported engine type: "{engine_class}"')
