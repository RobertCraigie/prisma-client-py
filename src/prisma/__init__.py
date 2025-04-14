# -*- coding: utf-8 -*-

__title__ = 'prisma'
__author__ = 'RobertCraigie'
__license__ = 'APACHE'
__copyright__ = 'Copyright 2020-2023 RobertCraigie'
__version__ = '0.15.0'

import sys as _sys
from typing import TYPE_CHECKING, Union

from . import errors as errors
from .utils import setup_logging
from ._types import PrismaMethod as PrismaMethod
from ._config import config as config
from ._metrics import (
    Metric as Metric,
    Metrics as Metrics,
    MetricHistogram as MetricHistogram,
)
from .validator import *

try:
    from .metadata import GENERATED_VERSION as _generated_version  # noqa: TID251

    GENERATED_VERSION: Union[str, None] = _generated_version
except ImportError:
    GENERATED_VERSION = None  # pyright: ignore[reportConstantRedefinition]

# the import ordering is important here because
# we rely on the fact that `prisma/client.py` is the
# first piece of generated code that is loaded. This is
# especially useful for `python -m prisma_cleanup`
try:
    from .client import *  # noqa: I001, TID251
    from .fields import *  # noqa: TID251
    from . import (
        bases as bases,  # noqa: TID251
        types as types,  # noqa: TID251
        models as models,  # noqa: TID251
        partials as partials,  # noqa: TID251
    )
except ModuleNotFoundError:
    # code has not been generated yet
    # TODO: this could swallow unexpected errors

    # we only define this magic function when the client has not
    # been generated for performance reasons and we hide it from
    # type checkers so that they don't incidentally disable type
    # checking due to the dynamic nature of the `__getattr__`
    # magic dunder method.
    if not TYPE_CHECKING:

        def __getattr__(name: str):
            try:
                return globals()[name]
            except KeyError as err:
                # TODO: support checking for 'models' here too
                if name in {'Prisma', 'Client'}:
                    raise RuntimeError(
                        "The Client hasn't been generated yet, "
                        'you must run `prisma generate` before you can use the client.\n'
                        'See https://prisma-client-py.readthedocs.io/en/stable/reference/troubleshooting/#client-has-not-been-generated-yet'
                    ) from None

                # leaves handling of this potential error to Python as per PEP 562
                raise AttributeError() from err
except Exception as exc:
    if GENERATED_VERSION == __version__:
        raise

    print('ignoring error during generated client import as the generated client is outdated', file=_sys.stderr)  # noqa: T201

setup_logging()
