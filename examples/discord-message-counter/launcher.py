import os
import logging
import contextlib
from typing import Iterator

from prisma.utils import async_run

from bot import bot


@contextlib.contextmanager
def setup_logging() -> Iterator[None]:
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        '[{levelname:<7}] {name}: {message}',
        style='{',
    )
    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    try:
        yield
    finally:
        handler.close()
        logger.removeHandler(handler)


def launch() -> None:
    with setup_logging():
        async_run(bot.prisma.connect())
        bot.run(os.environ['BOT_TOKEN'])


if __name__ == '__main__':
    launch()
