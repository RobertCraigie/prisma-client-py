import sys

if sys.version_info[:2] == (3, 6):
    # as far as I am aware the semantics of this are the same
    # on python 3.6
    from asyncio import get_event_loop as get_running_loop
else:
    from asyncio import (  # pylint: disable=no-name-in-module
        get_running_loop as get_running_loop,
    )
