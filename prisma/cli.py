# -*- coding: utf-8 -*-

import os
import sys
import logging
import subprocess
import contextlib
from typing import List, Iterator

from . import generator, jsonrpc, binaries


__all__ = ('main', 'setup_logging')

log = logging.getLogger(__name__)


def main() -> None:
    with setup_logging():
        args = sys.argv
        if len(args) > 1:
            run_prisma_command(args[1:])
        else:
            if not os.environ.get('PRISMA_GENERATOR_INVOCATION'):
                log.warning(
                    'This command is only meant to be invoked internally. '
                    'Please run the following instead:'
                )
                log.warning('`python3 -m prisma <command>`')
                log.warning('e.g.')
                log.warning('python3 -m prisma generate')
                sys.exit(1)

            invoke_prisma()


def run_prisma_command(args: List[str]) -> None:
    directory = binaries.ensure_cached()
    path = directory.joinpath(binaries.PRISMA_CLI_NAME)
    if not path.exists():
        raise RuntimeError(
            f'The Prisma CLI is not downloaded, expected {path} to exist.'
        )

    log.debug('Using Prisma CLI at %s', path)
    log.debug('Running command with args: %s', args)

    env = {'PRISMA_HIDE_UPDATE_MESSAGE': 'true', **os.environ}

    # ensure the client uses our engine binaries
    for engine in binaries.ENGINES:
        env[engine.env] = engine.location

    process = subprocess.run(  # pylint: disable=subprocess-run-check
        [str(path.absolute()), *args],
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    sys.exit(process.returncode)


@contextlib.contextmanager
def setup_logging(use_handler: bool = True) -> Iterator[None]:
    try:
        logger = logging.getLogger()

        # TODO: this does not log anything when running from the prisma cli
        if os.environ.get('PRISMA_PY_DEBUG'):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        if use_handler:
            fmt = logging.Formatter(
                '[{levelname:<7}] {name}: {message}',
                style='{',
            )
            handler = logging.StreamHandler()
            handler.setFormatter(fmt)
            logger.addHandler(handler)

        yield
    finally:
        if use_handler:
            handler.close()
            logger.removeHandler(handler)


def invoke_prisma() -> None:
    while True:
        line = jsonrpc.readline()
        if line is None:
            log.debug('Prisma invokation ending')
            break

        request = jsonrpc.parse(line)
        log.debug(
            'Received request method: %s with params: %s',
            request.method,
            request.params,
        )

        response = None
        if request.method == 'getManifest':
            response = jsonrpc.Response(
                id=request.id,
                result=dict(
                    manifest=jsonrpc.Manifest(
                        defaultOutput=str(generator.BASE_PACKAGE_DIR.absolute()),
                        prettyName='Prisma Client Py',
                    )
                ),
            )
        elif request.method == 'generate':
            if request.params is None:
                raise RuntimeError('Prisma JSONRPC did not send data to generate.')

            generator.run(request.params)
            response = jsonrpc.Response(id=request.id, result=None)
        else:
            raise RuntimeError(f'JSON RPC received unexpected method: {request.method}')

        if response is not None:
            jsonrpc.reply(response)


if __name__ == '__main__':
    main()
