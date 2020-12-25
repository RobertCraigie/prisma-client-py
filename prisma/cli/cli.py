# -*- coding: utf-8 -*-

import os
import sys
import logging
import contextlib

from .. import generator, jsonrpc


__all__ = ('main',)

log = logging.getLogger(__name__)


def main():
    with setup_logging():
        args = sys.argv
        if len(args) > 1:
            print('Prisma CLI has not been implemented yet.', file=sys.stderr)
            sys.exit(1)

        if not os.environ.get('PRISMA_GENERATOR_INVOCATION'):
            log.warning(
                'This command is only meant to be invoked internally. Please run the following instead:'
            )
            log.warning('`python3 -m prisma <command>`')
            log.warning('e.g.')
            log.warning('python3 -m prisma generate')
            sys.exit(1)

        invoke_prisma()


@contextlib.contextmanager
def setup_logging():
    try:
        logger = logging.getLogger()

        # TODO: this does not log anything when running from the prisma cli
        if os.environ.get('PRISMA_PY_DEBUG'):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        fmt = logging.Formatter(
            '[{levelname:<7}] {name}: {message}',
            style='{',
        )
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler())

        yield
    finally:
        handler.close()
        logger.removeHandler(handler)


def invoke_prisma():
    while True:
        try:
            line = jsonrpc.readline()
        except TimeoutError:
            log.debug('Timed out waiting for stdin input')
            return

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
            generator.run(request.params)
            response = jsonrpc.Response(id=request.id, result=None)
        else:
            raise RuntimeError(f'JSON RPC received unexpected method: {request.method}')

        if response is not None:
            jsonrpc.reply(response)


if __name__ == '__main__':
    main()
