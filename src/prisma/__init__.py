# -*- coding: utf-8 -*-

__title__ = 'prisma'
__author__ = 'RobertCraigie'
__license__ = 'APACHE'
__copyright__ = 'Copyright 2020-2021 RobertCraigie'
__version__ = '0.2.1'

from .utils import setup_logging
from . import errors as errors
from .validator import *


try:
    from .client import *
    from .fields import *
    from . import (
        models as models,
        partials as partials,
        types as types,
    )
except ModuleNotFoundError:
    # code has not been generated yet
    # TODO: this could swallow unexpected errors
    pass


setup_logging()
