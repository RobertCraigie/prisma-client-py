import asyncio
from prisma import Prisma
from functools import wraps
from datetime import timedelta
from typing import Any, Callable


__all__ = ('use_prisma',)

CLIENT_NAME_DEFAULT_VALUE: str = 'db'


def use_prisma(*args: Any, **kwargs: Any) -> Callable[..., Any]:
    """Decorator to provide an auto-connecting and auto-disconnecting Prisma client."""
    _CLIENT_NAME_KEY: str = 'name'

    def get_client_settings():
        """Return the appropriate settings based on provided arguments."""
        settings = {  # default client settings
            'connect_timeout': timedelta(seconds=30),
            'http': {'timeout': 600},
        }
        if not kwargs:
            return settings
        settings.update(kwargs)
        if _CLIENT_NAME_KEY in settings:
            del settings[_CLIENT_NAME_KEY]
        return settings

    def should_bypass(*f_args, **f_kwargs):
        """
        Check if the decorated function was called with a Prisma instance in the args or kwargs.
        If yes, return True, otherwise return False.
        In case of yes, we won't create a new Prisma instance.
        """
        for arg_list in [f_args, f_kwargs.values()]:
            for arg in arg_list:
                if isinstance(arg, Prisma):
                    return True
        return False

    def outer_wrapper(func):
        @wraps(func)
        async def wrapper(*f_args, **f_kwargs):
            if should_bypass(*f_args, **f_kwargs):
                return await func(*f_args, **f_kwargs)
            prisma = Prisma(**get_client_settings())
            await prisma.connect()
            try:
                f_kwargs[
                    kwargs.get(_CLIENT_NAME_KEY, CLIENT_NAME_DEFAULT_VALUE)
                ] = prisma
                return await func(*f_args, **f_kwargs)
            except (KeyboardInterrupt, asyncio.CancelledError):
                await prisma.disconnect()
            finally:
                await prisma.disconnect()

        return wrapper

    # distinguish between decorator usage with and without arguments
    if args and callable(args[0]):
        # no decorator arguments were provided
        return outer_wrapper(args[0])
    # decorator arguments were provided
    return outer_wrapper
