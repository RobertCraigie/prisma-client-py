import os
import time
import logging


def time_since(start: float, precision: int = 4) -> str:
    # TODO: prettier output
    delta = round(time.monotonic() - start, precision)
    return f'{delta}s'


def setup_logging() -> None:
    if os.environ.get('PRISMA_PY_DEBUG'):
        logging.getLogger('prisma').setLevel(logging.DEBUG)
