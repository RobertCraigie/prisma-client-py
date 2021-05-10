import asyncio
from datetime import datetime
from typing import Coroutine, Any, Optional, List, cast

import click
from click.testing import CliRunner, Result

from prisma.cli import main


class Runner:
    def __init__(self) -> None:
        self._runner = CliRunner()
        self.default_cli = None  # type: Optional[click.Command]

    def invoke(
        self,
        args: Optional[List[str]] = None,
        cli: Optional[click.Command] = None,
        **kwargs: Any
    ) -> Result:
        default_args: Optional[List[str]] = None

        if cli is not None:
            default_args = args
        elif self.default_cli is not None:
            cli = self.default_cli
            default_args = args
        else:

            @click.command()
            def cli() -> None:  # pylint: disable=function-redefined
                if args is not None:
                    # fake invocation context
                    args.insert(0, 'prisma')

                main(args, use_handler=False, do_cleanup=False, pipe=True)

            # mypy doesn't pick up the def properly
            cli = cast(click.Command, cli)

            # we don't pass any args to click as we need to parse them ourselves
            default_args = []

        return self._runner.invoke(cli, default_args, **kwargs)


def async_run(coro: Coroutine[Any, Any, Any]) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


def assert_time_like_now(dt: datetime, threshold: int = 10) -> None:
    # NOTE: I do not know if prisma datetimes are always in UTC
    #
    # have to remove the timezone details as utcnow() is not timezone aware
    # and we cannot subtract a timezone aware datetime from a non timezone aware datetime
    dt = dt.replace(tzinfo=None)
    delta = datetime.utcnow() - dt
    assert delta.days == 0
    assert delta.total_seconds() < threshold
