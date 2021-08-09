import os
import sys
import time
import socket
import logging
import subprocess
from pathlib import Path
from typing import NoReturn, Dict, Type, Any

from . import errors
from .. import errors as prisma_errors

from ..http import Response
from ..utils import time_since
from ..binaries import GLOBAL_TEMP_DIR, ENGINE_VERSION, platform


log: logging.Logger = logging.getLogger(__name__)
ERROR_MAPPING: Dict[str, Type[Exception]] = {
    'P2002': prisma_errors.UniqueViolationError,
    'P2010': prisma_errors.RawQueryError,
    'P2012': prisma_errors.MissingRequiredValueError,
    'P2021': prisma_errors.TableNotFoundError,
    'P2025': prisma_errors.RecordNotFoundError,
}


def ensure() -> Path:
    start_time = time.monotonic()
    file = None
    force_version = True
    binary_name = platform.check_for_extension(platform.binary_platform())

    name = f'prisma-query-engine-{binary_name}'
    local_path = Path.cwd().joinpath(name)
    global_path = GLOBAL_TEMP_DIR.joinpath(name)

    log.debug('Expecting local query engine %s', local_path)
    log.debug('Expecting global query engine %s', global_path)

    # TODO: this resolving should be moved to the binary class
    binary = os.environ.get('PRISMA_QUERY_ENGINE_BINARY')
    if binary:
        log.debug('PRISMA_QUERY_ENGINE_BINARY is defined, using %s', binary)

        if not Path(binary).exists():
            raise errors.BinaryNotFoundError(
                'PRISMA_QUERY_ENGINE_BINARY was provided, '
                f'but no query engine was found at {binary}'
            )

        file = Path(binary)
        force_version = False
    elif local_path.exists():
        file = local_path
        log.debug('Query engine found in the working directory')
    elif global_path.exists():
        file = global_path
        log.debug('Query engine found in the global path')

    if not file:
        raise errors.BinaryNotFoundError(
            f'Expected {local_path} or {global_path} but neither were found.\n'
            'Try running prisma py fetch'
        )

    start_version = time.monotonic()
    process = subprocess.run(
        [file.absolute(), '--version'], stdout=subprocess.PIPE, check=True
    )
    log.debug('Version check took %s', time_since(start_version))

    version = (
        str(process.stdout, sys.getdefaultencoding())
        .replace('query-engine', '')
        .strip()
    )
    log.debug('Using query engine version %s', version)

    if force_version and version != ENGINE_VERSION:
        raise errors.MismatchedVersionsError(expected=ENGINE_VERSION, got=version)

    log.debug('Using query engine at %s', file)
    log.debug('Ensuring query engine took: %s', time_since(start_time))

    return file


def get_open_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return int(port)


def handle_response_errors(resp: Response, data: Any) -> NoReturn:
    for error in data:
        try:
            user_facing = error.get('user_facing_error', {})
            code = user_facing.get('error_code')
            if code is None:
                continue

            exc = ERROR_MAPPING.get(code)
            if exc is not None:
                raise exc(error)

            if 'A value is required but not set' in user_facing.get('message', ''):
                raise prisma_errors.MissingRequiredValueError(error)
        except (KeyError, TypeError):
            continue

    try:
        raise prisma_errors.DataError(data[0])
    except (IndexError, TypeError):
        pass

    raise errors.EngineRequestError(
        resp, f'Could not process erroneous response: {data}'
    )
