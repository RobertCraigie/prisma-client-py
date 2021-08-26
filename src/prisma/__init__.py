# -*- coding: utf-8 -*-
# pyright: reportUnusedImport=false

__title__ = 'prisma'
__author__ = 'RobertCraigie'
__license__ = 'APACHE'
__copyright__ = 'Copyright 2020-2021 RobertCraigie'
__version__ = '0.0.3'

from .utils import setup_logging
from . import errors


try:
    from .client import *
    from . import models, partials, types
except ModuleNotFoundError:
    # code has not been generated yet
    # TODO: this could swallow unexpected errors
    pass


setup_logging()
