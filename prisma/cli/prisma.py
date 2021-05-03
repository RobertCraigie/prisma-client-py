import os
import sys
import logging
import subprocess
from typing import List, Union, Optional, IO

from .. import generator, jsonrpc, binaries


log = logging.getLogger(__name__)


def run(
    args: List[str],
    check: bool = False,
    pipe: bool = False,
) -> int:
    directory = binaries.ensure_cached()
    path = directory.joinpath(binaries.PRISMA_CLI_NAME)
    if not path.exists():
        raise RuntimeError(
            f'The Prisma CLI is not downloaded, expected {path} to exist.'
        )

    log.debug('Using Prisma CLI at %s', path)
    log.debug('Running prisma command with args: %s', args)

    env = {'PRISMA_HIDE_UPDATE_MESSAGE': 'true', **os.environ}

    # ensure the client uses our engine binaries
    for engine in binaries.ENGINES:
        env[engine.env] = str(engine.path.absolute())

    encoding = None  # type: Optional[str]
    stdout = sys.stdout  # type: Union[int, IO[str]]
    stderr = sys.stderr  # type: Union[int, IO[str]]

    if pipe:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
        encoding = 'utf-8'

    process = subprocess.run(
        [str(path.absolute()), *args],
        env=env,
        check=check,
        stdout=stdout,
        stderr=stderr,
        encoding=encoding,
    )

    if pipe:
        print(process.stdout)
        print(process.stderr, file=sys.stderr)

    return process.returncode


def invoke() -> None:
    while True:
        line = jsonrpc.readline()
        if line is None:
            log.debug('Prisma invocation ending')
            break

        request = jsonrpc.parse(line)
        log.debug(
            'Received request method: %s',
            request.method,
        )

        # TODO: this can hang the prisma process if an error occurs
        response = None
        if request.method == 'getManifest':
            response = jsonrpc.Response(
                id=request.id,
                result=dict(
                    manifest=jsonrpc.Manifest(
                        defaultOutput=str(generator.BASE_PACKAGE_DIR.absolute()),
                        prettyName='Prisma Client Python',
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
