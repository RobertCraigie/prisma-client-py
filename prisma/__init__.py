# -*- coding: utf-8 -*-

__title__ = 'prisma'
__author__ = 'RobertCraigie'
__license__ = 'APACHE'
__copyright__ = 'Copyright 2020-2021 RobertCraigie'
__version__ = '0.0.1'

from .plugins import *
from .utils import setup_logging


try:
    from .client import *
except ModuleNotFoundError:
    # code has not been generated yet
    # TODO: this could swallow unexpected errors
    pass


setup_logging()
